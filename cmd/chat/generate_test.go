package main

import (
	"context"
	"errors"
	"net"
	"sync/atomic"
	"testing"
	"time"

	"github.com/cloudwego/eino/components/model"
	"github.com/cloudwego/eino/schema"
)

type mockToolCallingChatModel struct {
	generateFn func(context.Context, []*schema.Message, ...model.Option) (*schema.Message, error)
	streamFn   func(context.Context, []*schema.Message, ...model.Option) (*schema.StreamReader[*schema.Message], error)
	withToolsFn func([]*schema.ToolInfo) (model.ToolCallingChatModel, error)
}

func (m *mockToolCallingChatModel) Generate(ctx context.Context, input []*schema.Message, opts ...model.Option) (*schema.Message, error) {
	if m.generateFn != nil {
		return m.generateFn(ctx, input, opts...)
	}
	return nil, errors.New("generateFn not set")
}

func (m *mockToolCallingChatModel) Stream(ctx context.Context, input []*schema.Message, opts ...model.Option) (*schema.StreamReader[*schema.Message], error) {
	if m.streamFn != nil {
		return m.streamFn(ctx, input, opts...)
	}
	return nil, errors.New("streamFn not set")
}

func (m *mockToolCallingChatModel) WithTools(tools []*schema.ToolInfo) (model.ToolCallingChatModel, error) {
	if m.withToolsFn != nil {
		return m.withToolsFn(tools)
	}
	return m, nil
}

type fakeNetError struct {
	msg       string
	timeout   bool
	temporary bool
}

func (e *fakeNetError) Error() string   { return e.msg }
func (e *fakeNetError) Timeout() bool   { return e.timeout }
func (e *fakeNetError) Temporary() bool { return e.temporary }

func TestGenerateSuccess(t *testing.T) {
	message := schema.AssistantMessage("hello", nil)
	mockModel := &mockToolCallingChatModel{
		generateFn: func(context.Context, []*schema.Message, ...model.Option) (*schema.Message, error) {
			return message, nil
		},
	}

	got, err := generate(context.Background(), mockModel, nil)
	if err != nil {
		t.Fatalf("generate returned unexpected error: %v", err)
	}

	if got != message {
		t.Fatalf("expected message %p, got %p", message, got)
	}
}

func TestGenerateError(t *testing.T) {
	baseErr := errors.New("boom")
	mockModel := &mockToolCallingChatModel{
		generateFn: func(context.Context, []*schema.Message, ...model.Option) (*schema.Message, error) {
			return nil, baseErr
		},
	}

	got, err := generate(context.Background(), mockModel, nil)
	if got != nil {
		t.Fatalf("expected nil message, got %v", got)
	}
	if err == nil || !errors.Is(err, baseErr) {
		t.Fatalf("expected error wrapping base error: %v", err)
	}
}

func TestGenerateWithRetry_SucceedsAfterRetry(t *testing.T) {
	message := schema.AssistantMessage("retry", nil)
	var calls atomic.Int32
	firstErr := &fakeNetError{msg: "temporary", temporary: true}

	mockModel := &mockToolCallingChatModel{
		generateFn: func(context.Context, []*schema.Message, ...model.Option) (*schema.Message, error) {
			if calls.Add(1) == 1 {
				return nil, firstErr
			}
			return message, nil
		},
	}

	prevDelay := retryBaseDelay
	retryBaseDelay = time.Millisecond
	t.Cleanup(func() {
		retryBaseDelay = prevDelay
	})

	got, err := generateWithRetry(context.Background(), mockModel, nil)
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if got != message {
		t.Fatalf("expected message %p, got %p", message, got)
	}
	if calls.Load() != 2 {
		t.Fatalf("expected 2 generate attempts, got %d", calls.Load())
	}
}

func TestGenerateWithRetry_NonRetryable(t *testing.T) {
	baseErr := errors.New("fatal")
	var calls atomic.Int32
	mockModel := &mockToolCallingChatModel{
		generateFn: func(context.Context, []*schema.Message, ...model.Option) (*schema.Message, error) {
			calls.Add(1)
			return nil, baseErr
		},
	}

	_, err := generateWithRetry(context.Background(), mockModel, nil)
	if err == nil || !errors.Is(err, baseErr) {
		t.Fatalf("expected error wrapping baseErr, got %v", err)
	}
	if calls.Load() != 1 {
		t.Fatalf("expected 1 generate attempt, got %d", calls.Load())
	}
}

func TestGenerateWithRetry_ContextCanceled(t *testing.T) {
	var calls atomic.Int32
	mockModel := &mockToolCallingChatModel{
		generateFn: func(context.Context, []*schema.Message, ...model.Option) (*schema.Message, error) {
			calls.Add(1)
			return nil, &fakeNetError{msg: "timeout", timeout: true}
		},
	}

	prevDelay := retryBaseDelay
	retryBaseDelay = time.Millisecond
	t.Cleanup(func() {
		retryBaseDelay = prevDelay
	})

	ctx, cancel := context.WithCancel(context.Background())
	go func() {
		// ensure cancellation happens after first attempt
		time.Sleep(time.Millisecond)
		cancel()
	}()

	_, err := generateWithRetry(ctx, mockModel, nil)
	if err == nil || !errors.Is(err, context.Canceled) {
		t.Fatalf("expected context canceled error, got %v", err)
	}
	if calls.Load() == 0 {
		t.Fatalf("expected at least one generate attempt")
	}
}

func TestStreamSuccess(t *testing.T) {
	reader, writer := schema.Pipe[*schema.Message](1)
	writer.Close()
	mockModel := &mockToolCallingChatModel{
		streamFn: func(context.Context, []*schema.Message, ...model.Option) (*schema.StreamReader[*schema.Message], error) {
			return reader, nil
		},
	}

	got, err := stream(context.Background(), mockModel, nil)
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if got != reader {
		t.Fatalf("expected reader %p, got %p", reader, got)
	}
}

func TestStreamError(t *testing.T) {
	baseErr := errors.New("stream error")
	mockModel := &mockToolCallingChatModel{
		streamFn: func(context.Context, []*schema.Message, ...model.Option) (*schema.StreamReader[*schema.Message], error) {
			return nil, baseErr
		},
	}

	got, err := stream(context.Background(), mockModel, nil)
	if got != nil {
		t.Fatalf("expected nil stream reader, got %v", got)
	}
	if err == nil || !errors.Is(err, baseErr) {
		t.Fatalf("expected error wrapping baseErr, got %v", err)
	}
}

func TestIsRetryableError(t *testing.T) {
	tests := []struct {
		name string
		err  error
		want bool
	}{
		{"nil", nil, false},
		{"timeout", &fakeNetError{timeout: true}, true},
		{"temporary", &fakeNetError{temporary: true}, true},
		{"nonRetryableNet", &fakeNetError{}, false},
		{"generic", errors.New("other"), false},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			if got := isRetryableError(tt.err); got != tt.want {
				t.Fatalf("isRetryableError(%v) = %v, want %v", tt.err, got, tt.want)
			}
		})
	}
}

func TestIsRetryableError_ImplementsNetError(t *testing.T) {
	var _ net.Error = &fakeNetError{}
}
