package main

import (
	"context"
	"log"
	"os"

	"github.com/cloudwego/eino-ext/components/model/openai"
	"github.com/cloudwego/eino/components/model"
)

func createOpenAIChatModel(ctx context.Context) model.ToolCallingChatModel {
	key := os.Getenv("OPENAI_API_KEY")
	modelName := os.Getenv("OPENAI_MODEL_NAME")
	baseURL := os.Getenv("OPENAI_BASE_URL")
	temperature := float32(0.0)

	chatModel, err := openai.NewChatModel(ctx, &openai.ChatModelConfig{
		APIKey:      key,
		Model:       modelName,
		BaseURL:     baseURL,
		Temperature: &temperature,
	})
	if err != nil {
		log.Fatalf("failed to create openai chat model: %v", err)
	}
	return chatModel
}
