package main

import (
	"context"
	"fmt"
	"io"
	"os"

	"github.com/cloudwego/eino/schema"
)

func reportStream(sr *schema.StreamReader[*schema.Message]) error {
	return reportStreamWithContext(context.Background(), sr, os.Stdout)
}

func reportStreamWithContext(ctx context.Context, sr *schema.StreamReader[*schema.Message], writer io.Writer) error {
	sr.SetAutomaticClose()

	// 创建一个通道来监听上下文取消
	done := make(chan struct{})
	defer close(done)

	// 启动一个goroutine来监听上下文取消
	go func() {
		select {
		case <-done:
			return
		case <-ctx.Done():
			sr.Close()
			return
		}
	}()

	for {
		chunk, err := sr.Recv()
		if err == io.EOF {
			return nil
		}
		if err != nil {
			return fmt.Errorf("stream error: %w", err)
		}
		if chunk != nil && chunk.Content != "" {
			if _, err := fmt.Fprint(writer, chunk.Content); err != nil {
				return fmt.Errorf("write error: %w", err)
			}
		}
	}
}
