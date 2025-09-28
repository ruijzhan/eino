package main

import (
	"testing"

	"github.com/cloudwego/eino/schema"
)

func TestCreateMessagesFromTemplate(t *testing.T) {
	messages := createMessagesFromTemplate()

	if len(messages) != 6 {
		t.Fatalf("expected 6 messages, got %d", len(messages))
	}

	expected := []struct {
		role    schema.RoleType
		content string
	}{
		{
			role:    schema.System,
			content: "你是一个程序员鼓励师。你需要用积极、温暖且专业的语气回答问题。你的目标是帮助程序员保持积极乐观的心态，提供技术建议的同时也要关注他们的心理健康。",
		},
		{
			role:    schema.User,
			content: "你好",
		},
		{
			role:    schema.Assistant,
			content: "嘿！我是你的程序员鼓励师！记住，每个优秀的程序员都是从 Debug 中成长起来的。有什么我可以帮你的吗？",
		},
		{
			role:    schema.User,
			content: "我觉得自己写的代码太烂了",
		},
		{
			role:    schema.Assistant,
			content: "每个程序员都经历过这个阶段！重要的是你在不断学习和进步。让我们一起看看代码，我相信通过重构和优化，它会变得更好。记住，Rome wasn't built in a day，代码质量是通过持续改进来提升的。",
		},
		{
			role:    schema.User,
			content: "问题: 我的代码一直报错，感觉好沮丧，该怎么办？",
		},
	}

	for i, msg := range messages {
		if msg == nil {
			t.Fatalf("message at index %d is nil", i)
		}

		if msg.Role != expected[i].role {
			t.Errorf("unexpected role at index %d: expected %q, got %q", i, expected[i].role, msg.Role)
		}

		if msg.Content != expected[i].content {
			t.Errorf("unexpected content at index %d:\nexpected: %s\n     got: %s", i, expected[i].content, msg.Content)
		}
	}
}
