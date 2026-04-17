/* © 2026 Dre's Autonomous Neural Interface | Professional Grade Asset */
/* 
 * realtime_client.go - Industrial Pure Protocol Client
 * Engineered for maximum hardware efficiency and low latency.
 * Implements Phoenix Channels 2.0.0 via native WebSockets.
 */

package main

import (
	"encoding/json"
	"fmt"
	"log"
	"net/url"
	"time"

	"github.com/gorilla/websocket"
)

// PhoenixMessage represents the standard Phoenix protocol envelope
type PhoenixMessage struct {
	Topic   string      `json:"topic"`
	Event   string      `json:"event"`
	Payload interface{} `json:"payload"`
	Ref     string      `json:"ref"`
}

// RealtimeClient manages a low-latency connection to a Phoenix-compatible server (Supabase)
type RealtimeClient struct {
	Conn   *websocket.Conn
	ApiKey string
	URL    string
	Logger *log.Logger
}

// NewRealtimeClient initializes a new Industrial Client
func NewRealtimeClient(projectRef, apiKey string, logger *log.Logger) *RealtimeClient {
	u := url.URL{
		Scheme:   "wss",
		Host:     projectRef + ".supabase.co",
		Path:     "/realtime/v1/websocket",
		RawQuery: "apikey=" + apiKey,
	}
	return &RealtimeClient{
		URL:    u.String(),
		ApiKey: apiKey,
		Logger: logger,
	}
}

// Connect establishes the primary neural bind to the socket server
func (c *RealtimeClient) Connect() error {
	var err error
	c.Conn, _, err = websocket.DefaultDialer.Dial(c.URL, nil)
	if err != nil {
		return fmt.Errorf("[DRE-NEURAL] Connection Fault: %w", err)
	}
	c.Logger.Println("[DRE-NEURAL] Bound to Socket Engine. Industrial Protocol ACTIVE.")

	// Start the 25s Heartbeat Loop as per Studio Standards
	go c.heartbeatLoop()

	return nil
}

// heartbeatLoop maintains connection persistence with the Phoenix server
func (c *RealtimeClient) heartbeatLoop() {
	ticker := time.NewTicker(25 * time.Second)
	defer ticker.Stop()

	for range ticker.C {
		msg := PhoenixMessage{
			Topic:   "phoenix",
			Event:   "heartbeat",
			Payload: map[string]interface{}{},
			Ref:     fmt.Sprintf("%d", time.Now().Unix()),
		}
		if err := c.Conn.WriteJSON(msg); err != nil {
			c.Logger.Printf("[DRE-NEURAL] Heartbeat Failure: %v", err)
			return
		}
	}
}

// JoinChannel initiates a phx_join event for a specific topic
func (c *RealtimeClient) JoinChannel(topic string, config map[string]interface{}) error {
	msg := PhoenixMessage{
		Topic:   topic,
		Event:   "phx_join",
		Payload: config,
		Ref:     "1",
	}
	c.Logger.Printf("[DRE-NEURAL] Joining Channel: %s", topic)
	return c.Conn.WriteJSON(msg)
}

// Listen processes incoming messages and logs them to the forensic stream
func (c *RealtimeClient) Listen(handler func(msg PhoenixMessage)) {
	for {
		_, raw, err := c.Conn.ReadMessage()
		if err != nil {
			c.Logger.Printf("[DRE-NEURAL] Protocol Break: %v", err)
			return
		}

		var incoming PhoenixMessage
		if err := json.Unmarshal(raw, &incoming); err != nil {
			c.Logger.Printf("[DRE-NEURAL] Decode Error: %v", err)
			continue
		}

		handler(incoming)
	}
}
