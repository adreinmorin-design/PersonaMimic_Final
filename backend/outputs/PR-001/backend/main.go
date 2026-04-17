/* © 2026 Dre's Autonomous Neural Interface | Professional Grade Asset */
/*
 * Mission Control Backend - Forged Industrial Code
 * Archetype: supabase_realtime + pure_phoenix_2.0
 */

package main

import (
	"fmt"
	"log"
	"os"
	"os/signal"
	"time"
)

func main() {
	// Professional Headers
	fmt.Println("==================================================")
	fmt.Println("🏭 DRE NEURAL SWARM: MISSION CONTROL v2.0")
	fmt.Println("==================================================")

	projectRef := os.Getenv("SUPABASE_PROJECT_REF")
	apiKey := os.Getenv("SUPABASE_API_KEY")

	if projectRef == "" || apiKey == "" {
		log.Fatal("[MISSION-CONTROL] Environmental Fault: SUPABASE_PROJECT_REF or SUPABASE_API_KEY missing.")
	}

	dreLogger := log.New(os.Stdout, "[DRE-LOG] ", log.LstdFlags)

	client := NewRealtimeClient(projectRef, apiKey, dreLogger)
	
	dreLogger.Printf("Attempting Neural Bind to %s", projectRef)
	
	if err := client.Connect(); err != nil {
		log.Fatal("[MISSION-CONTROL] Dial Failure: ", err)
	}

	// Join Industrial Monitoring Channel with Postgres CDC Config
	joinConfig := map[string]interface{}{
		"config": map[string]interface{}{
			"postgres_changes": []map[string]interface{}{
				{"event": "*", "schema": "public", "table": "sensors"},
			},
		},
	}
	
	if err := client.JoinChannel("realtime:public:factory_sensors", joinConfig); err != nil {
		log.Fatal("[MISSION-CONTROL] Join Failure: ", err)
	}

	dreLogger.Println("BOUND: Monitoring 'factory_sensors' via Pure Protocol.")

	// Event Processor
	interrupt := make(chan os.Signal, 1)
	signal.Notify(interrupt, os.Interrupt)

	go client.Listen(func(incoming PhoenixMessage) {
		// Forensic Log - Industrial Standard
		if incoming.Event == "postgres_changes" {
			fmt.Printf("[SENSOR-DATA] [%s] %v\n", time.Now().Format(time.RFC3339), incoming.Payload)
		}
	})

	<-interrupt
	dreLogger.Println("Graceful Shutdown Sequence Engaged.")
}
