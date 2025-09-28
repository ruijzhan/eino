package main

import (
	"context"
	"errors"
	"fmt"
	"log"
	"net"
	"time"

	"github.com/cloudwego/eino/components/model"
	"github.com/cloudwego/eino/schema"
)

var retryBaseDelay = time.Second

func generate(ctx context.Context, llm model.ToolCallingChatModel, in []*schema.Message) (*schema.Message, error) {
	start := time.Now()
	out, err := llm.Generate(ctx, in)
	duration := time.Since(start)

	if err != nil {
		log.Printf("generate failed after %v: %v", duration, err)
		return nil, fmt.Errorf("llm generate failed: %w", err)
	}

	log.Printf("generate completed in %v", duration)
	return out, nil
}

func generateWithRetry(ctx context.Context, llm model.ToolCallingChatModel, in []*schema.Message) (*schema.Message, error) {
	const maxRetries = 3

	for attempt := 0; attempt < maxRetries; attempt++ {
		out, err := llm.Generate(ctx, in)
		if err == nil {
			if attempt > 0 {
				log.Printf("generate succeeded on retry attempt %d", attempt+1)
			}
			return out, nil
		}

		if isRetryableError(err) && attempt < maxRetries-1 {
			delay := retryBaseDelay * time.Duration(attempt+1)
			log.Printf("generate attempt %d failed: %v, retrying in %v", attempt+1, err, delay)
			select {
			case <-time.After(delay):
			case <-ctx.Done():
				return nil, fmt.Errorf("generate retry canceled: %w", ctx.Err())
			}
			continue
		}

		return nil, fmt.Errorf("after %d retries: %w", attempt+1, err)
	}

	return nil, errors.New("generateWithRetry: unexpected error")
}

func stream(ctx context.Context, llm model.ToolCallingChatModel, in []*schema.Message) (*schema.StreamReader[*schema.Message], error) {
	start := time.Now()
	stream, err := llm.Stream(ctx, in)
	duration := time.Since(start)

	if err != nil {
		log.Printf("stream failed after %v: %v", duration, err)
		return nil, fmt.Errorf("llm stream failed: %w", err)
	}

	log.Printf("stream started in %v", duration)
	return stream, nil
}

func isRetryableError(err error) bool {
	if err == nil {
		return false
	}

	var netErr net.Error
	if errors.As(err, &netErr) {
		return netErr.Timeout() || netErr.Temporary()
	}

	return false
}
