package main

import (
	"io"
	"log"

	"github.com/cloudwego/eino/schema"
)

func reportStream(sr *schema.StreamReader[*schema.Message]) {
	sr.SetAutomaticClose()
	i := 0
	for {
		chunk, err := sr.Recv()
		if err == io.EOF {
			return
		}
		if err != nil {
			log.Fatalf("stream error: %v", err)
		}
		if chunk == nil {
			log.Printf("stream chunk %d: <nil>", i)
			i++
			continue
		}
		log.Printf("%s", chunk.Content)
		i++
	}
}
