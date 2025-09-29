package main

import (
	"context"
	"errors"
	"fmt"
	"log"
	"os"
	"time"

	"github.com/cloudwego/eino-ext/components/model/openai"
	"github.com/cloudwego/eino/components/model"
)

// ModelConfig 模型配置
type ModelConfig struct {
	APIKey      string
	Model       string
	BaseURL     string
	Temperature *float32
	Timeout     time.Duration
	MaxRetries  int
}

// DefaultModelConfig 返回默认模型配置
func DefaultModelConfig() *ModelConfig {
	temperature := float32(0.7) // 默认创造性温度
	return &ModelConfig{
		Temperature: &temperature,
		Timeout:     30 * time.Second,
		MaxRetries:  3,
	}
}

// LoadModelConfig 从环境变量加载模型配置
func LoadModelConfig() (*ModelConfig, error) {
	config := DefaultModelConfig()

	// API密钥验证
	if key := os.Getenv("OPENAI_API_KEY"); key == "" {
		return nil, errors.New("OPENAI_API_KEY environment variable is required")
	} else {
		config.APIKey = key
	}

	// 模型名称验证
	if modelName := os.Getenv("OPENAI_MODEL_NAME"); modelName == "" {
		return nil, errors.New("OPENAI_MODEL_NAME environment variable is required")
	} else {
		config.Model = modelName
	}

	// 可选的 BaseURL
	if baseURL := os.Getenv("OPENAI_BASE_URL"); baseURL != "" {
		config.BaseURL = baseURL
	}

	// 可选的温度设置
	if tempStr := os.Getenv("OPENAI_TEMPERATURE"); tempStr != "" {
		var temperature float32
		if _, err := fmt.Sscanf(tempStr, "%f", &temperature); err != nil {
			return nil, fmt.Errorf("invalid OPENAI_TEMPERATURE value: %w", err)
		}
		config.Temperature = &temperature
	}

	// 可选的超时设置
	if timeoutStr := os.Getenv("OPENAI_TIMEOUT"); timeoutStr != "" {
		if timeout, err := time.ParseDuration(timeoutStr); err != nil {
			return nil, fmt.Errorf("invalid OPENAI_TIMEOUT value: %w", err)
		} else {
			config.Timeout = timeout
		}
	}

	// 可选的重试次数
	if maxRetriesStr := os.Getenv("OPENAI_MAX_RETRIES"); maxRetriesStr != "" {
		if maxRetries, err := fmt.Sscanf(maxRetriesStr, "%d", &config.MaxRetries); err != nil || maxRetries < 0 {
			return nil, fmt.Errorf("invalid OPENAI_MAX_RETRIES value: %w", err)
		}
	}

	return config, nil
}

func createOpenAIChatModel(ctx context.Context) model.ToolCallingChatModel {
	return createOpenAIChatModelWithConfig(ctx, nil)
}

func createOpenAIChatModelWithConfig(ctx context.Context, customConfig *ModelConfig) model.ToolCallingChatModel {
	var config *ModelConfig
	var err error

	// 使用自定义配置或从环境变量加载
	if customConfig != nil {
		config = customConfig
	} else {
		config, err = LoadModelConfig()
		if err != nil {
			log.Fatalf("failed to load model config: %v", err)
		}
	}

	// 创建上下文，包含超时
	ctxWithTimeout, cancel := context.WithTimeout(ctx, config.Timeout)
	defer cancel()

	// 带重试的模型创建
	var chatModel model.ToolCallingChatModel
	for attempt := 0; attempt <= config.MaxRetries; attempt++ {
		chatModel, err = openai.NewChatModel(ctxWithTimeout, &openai.ChatModelConfig{
			APIKey:      config.APIKey,
			Model:       config.Model,
			BaseURL:     config.BaseURL,
			Temperature: config.Temperature,
		})

		if err == nil {
			if attempt > 0 {
				log.Printf("model created successfully after %d attempts", attempt+1)
			}
			return chatModel
		}

		// 如果是最后一次尝试，记录错误
		if attempt == config.MaxRetries {
			log.Fatalf("failed to create openai chat model after %d attempts: %v", config.MaxRetries+1, err)
		}

		// 等待后重试
		wait := time.Duration(attempt+1) * time.Second
		log.Printf("model creation attempt %d failed: %v, retrying in %v", attempt+1, err, wait)
		time.Sleep(wait)
	}

	// 理论上不会到达这里，但为了完整性
	panic("unreachable")
}
