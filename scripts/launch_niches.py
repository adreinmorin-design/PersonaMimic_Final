import requests
import time

# The 4 high-conversion niches provided by the user
NICHES = [
    {
        "niche": "Specialized Prompt Libraries",
        "goal": "Create industry-specific prompt tasks (e.g., Prompts for Medical Coding, Lawyer's Guide to AI Briefing) designed for immediate utility and high-value problem solving."
    },
    {
        "niche": "Notion Ecosystems",
        "goal": "Build full 'Second Brain' systems for specific professions like Real Estate, Project Management, or Pet Care Management, rather than simple trackers."
    },
    {
        "niche": "Video Content Frameworks",
        "goal": "Synthesize short-form video scripts with strong Hooks and CTAs specifically for TikTok, Reels, and YouTube Shorts—designed for high conversion and engagement."
    },
    {
        "niche": "Micro-Learning Ebooks",
        "goal": "Draft ebooks solving specific, painful problems in under 20 minutes of reading, tailored for micro-learning and quick deployment."
    }
]

def launch_all():
    print("==========================================================")
    print("Initiating PersonaMimic Swarm - High Conversion Niches")
    print("==========================================================")
    
    webhook_url = "http://localhost:5678/webhook/trigger-mission"
    
    for item in NICHES:
        print(f"\n[+] Dispatching Mission: {item['niche']}")
        try:
            # We use the n8n webhook we just activated to route the mission to the MasterBrain
            response = requests.post(webhook_url, json=item, timeout=10)
            if response.status_code == 200:
                print(" -> Successfully injected into n8n Industrial Loop!")
            else:
                print(f" -> Failed to inject. n8n responded with HTTP {response.status_code}")
                print(f" -> {response.text}")
        except requests.exceptions.ConnectionError:
            print(" -> [ERROR] Could not connect to n8n webhook. Is Docker and the n8n container running?")
            break
        except Exception as e:
            print(f" -> [ERROR] {e}")
        
        # Short delay between dispatching swarm agents
        time.sleep(3)
        
    print("\nMission dispatch complete.")

if __name__ == "__main__":
    launch_all()
