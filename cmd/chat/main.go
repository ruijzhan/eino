package main

import (
	"context"
	"log"
)

func main() {
	ctx := context.Background()

	messages := createMessagesFromTemplate()

	cm := createOpenAIChatModel(ctx)

	result, err := generate(ctx, cm, messages)
	if err != nil {
		log.Fatalf("generate failed: %v", err)
	}
	log.Printf("generate result: %v", result)

	sr, err := stream(ctx, cm, messages)
	if err != nil {
		log.Fatalf("stream failed: %v", err)
	}
	reportStream(sr)
}
