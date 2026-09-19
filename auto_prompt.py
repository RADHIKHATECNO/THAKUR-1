import os
import sys
import math
import re
import time
import json
import urllib.request
from openai import OpenAI

STORY_FILE = "story.txt"
PROMPT_FILE = "prompts.txt"
METADATA_FILE = "metadata.txt"

API_KEY = os.getenv("OPENROUTER_API_KEY")
if not API_KEY:
    print("❌ ERROR: OPENROUTER_API_KEY is missing!")
    sys.exit(1)

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=API_KEY)

def get_live_free_models():
    # Yeh function best free models ki list nikalega
    models_list = []
    try:
        req = urllib.request.Request("https://openrouter.ai/api/v1/models")
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode('utf-8'))
        models_list = [m["id"] for m in data.get("data", []) if m.get("pricing", {}).get("prompt") == "0" and m.get("pricing", {}).get("completion") == "0"]
    except:
        pass
        
    # Guaranteed Fallback Models (Agar API se list na mile)
    fallbacks = [
        "google/gemini-2.0-flash-lite-preview-02-05:free", 
        "meta-llama/llama-3.3-70b-instruct:free",
        "cognitivecomputations/dolphin3.0-r1-mistral-24b:free",
        "meta-llama/llama-3.2-3b-instruct:free"
    ]
    
    # Dono lists ko combine kar dete hain
    for fb in fallbacks:
        if fb not in models_list:
            models_list.append(fb)
            
    return models_list

def generate_ai_script(duration_sec, topic):
    target_scenes = max(2, math.ceil(int(duration_sec) / 5))
    system_prompt = "You are a Master Visual Storyteller. You strictly follow instructions. Output ONLY the raw prompt lines. NO tables, NO intro, NO outro."
    
    user_prompt = f"""Task: Create a COMPLETE, highly engaging, and 100% YOUTUBE-SAFE visual story based on: "{topic}".
    Total Duration: {duration_sec} seconds. Generate EXACTLY {target_scenes} scenes.

    🚨 5-SECOND HOOK (CRITICAL):
    - The VERY FIRST SCENE must be visually shocking, mysterious, highly emotional, or fast-action to instantly GRAB the viewer's attention. Make them stop scrolling!

    🚨 DYNAMIC MOOD & GENRE:
    - Match the lighting, facial expressions, and foley audio exactly to the mood of the topic (e.g., Sad=gloomy/crying, Action=intense/fast, Romantic=sunset/warm, Horror=dark/nervous).

    🚨 YOUTUBE RULES: NO blood, NO weapons, NO gore. Family-Friendly only.
    🚨 STORY ARC: Scene 1 is the HOOK. Middle is action/struggle. Last Scene is a clear ENDING/RESOLUTION.
    🚨 BACKGROUND CONSISTENCY: Invent ONE specific character and ONE specific background. Keep them the SAME in every prompt.
    🚨 AUDIO RULES: ONLY Foley sounds. End every video prompt with "NO BGM, NO VOICE."

    FORMAT EXACTLY LIKE THIS EXAMPLE (Use the `|` symbol):
    A fluffy white wolf pup named Leo in a snowy mountain looking shocked | Loud wind howling, sudden snow crunching. NO BGM, NO VOICE.
    A fluffy white wolf pup named Leo in a snowy mountain slipping on ice | Rapid sliding sounds, panicked scratching. NO BGM, NO VOICE.

    START YOUR RESPONSE DIRECTLY WITH THE FIRST SCENE:"""
    
    models = get_live_free_models()
    attempt = 1
    max_attempts = 10 # Script jab tak nahi banegi, 10 baar tak alag-alag model try karega!

    for model_name in models:
        for _ in range(2): # Ek model ko 2 baar mauka dega
            if attempt > max_attempts:
                print("❌ ERROR: 10 attempts ho gaye par kisi AI ne sahi format nahi diya. Exiting.")
                return None
                
            print(f"🔄 Attempt {attempt}/{max_attempts} - Trying model: {model_name}...")
            try:
                response = client.chat.completions.create(
                    model=model_name,
                    messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}],
                    temperature=0.8
                )
                text = response.choices[0].message.content
                
                if text:
                    print("\n--- RAW AI OUTPUT ---")
                    print(text)
                    print("---------------------\n")
                    
                    valid_lines = []
                    for line in text.split('\n'):
                        line = line.strip()
                        line = re.sub(r'^[\d\.\-\*\s]+', '', line) # Galti se aaye numbers hidayega
                        if '|' in line and '---|' not in line and not line.startswith('|'):
                            valid_lines.append(line)
                            
                    if len(valid_lines) > 0:
                        print(f"✅ Success! Hamein {len(valid_lines)} valid scenes mil gaye from {model_name}.")
                        return "\n".join(valid_lines[:target_scenes])
                    else:
                        print(f"⚠️ AI ne script di, par format galat tha (No `|` found). Retrying...")
            except Exception as e:
                print(f"⚠️ Model {model_name} failed/crashed: {e}. Switching model...")
                time.sleep(2)
                
            attempt += 1

    return None

def generate_ai_metadata(topic):
    system_prompt = """You are a Top-Tier YouTube Shorts Growth Hacker & Viral Content Strategist.
You have personally analyzed THOUSANDS of the highest-viewed viral YouTube Shorts (10M+ views) 
across every niche - emotional stories, animal stories, moral stories, drama, motivation etc.
You know EXACTLY the proven psychological patterns, hook-words, curiosity-gaps, emoji placement, 
and hashtag strategy that makes the YouTube Algorithm push a video into the Shorts Suggestion Feed.
You NEVER write generic/boring metadata. You always replicate PROVEN VIRAL PATTERNS."""

    user_prompt = f"""Our Story Topic: "{topic}"

STEP 1 (Do this mentally): Think like you already studied the TOP 20 most viral YouTube Shorts 
that are similar in genre/emotion to this story topic. Identify what made THEIR titles, 
descriptions and tags rank in Suggested/Shorts feed (curiosity hook, emotional trigger words, 
numbers, power words, relatable phrasing, trending hashtags like #shorts #viral #fyp #trending).

STEP 2: Now create BRAND NEW, HIGHLY VIRAL, SEO-OPTIMIZED metadata for OUR story above, 
using the SAME proven viral formula you identified — but 100% relevant & matching to OUR topic 
(do not use unrelated clickbait, keep it honest to the story).

RULES:
- TITLE: Max 70 characters. MUST include a curiosity hook / emotional trigger / power word 
  (e.g. "You Won't Believe", "This Broke My Heart", "Wait Till The End", "POV:", "This Is Why...").
  Add 1-2 relevant emojis. Must feel like a viral Shorts title, NOT generic.
- DESC: 2-3 lines. FIRST line must hook curiosity (this is what shows before "...more" on Shorts).
  Include a soft call-to-action (like "Watch till the end 👀" or "Follow for more"). 
  End with 4-6 relevant hashtags mixing BROAD (#shorts #viral #fyp #trending) 
  AND NICHE-SPECIFIC hashtags related to the story topic.
- TAGS: Give 12-15 comma separated tags. Mix of:
   a) Broad viral tags (shorts, viral shorts, trending shorts, viral video, fyp)
   b) Niche/genre tags matching the story (e.g. emotional story, animal story, moral story, sad story, motivational shorts - pick whichever fits)
   c) Topic-specific keyword tags directly related to "{topic}"
- MUSIC: One unique 5-8 word background music mood description matching story's emotion.

OUTPUT FORMAT EXACTLY (no extra text, no explanation):
TITLE: [title]
DESC: [description with hashtags]
TAGS: [tag1, tag2, tag3, ...]
MUSIC: [music mood prompt]"""

    models = get_live_free_models()
    music_prompt = "dark emotional cinematic background score"

    for model_name in models[:3]:
        try:
            print(f"🎵 Generating VIRAL Metadata using {model_name}...")
            response = client.chat.completions.create(
                model=model_name,
                messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}],
                temperature=0.9
            )
            text = response.choices[0].message.content

            title_match = re.search(r"TITLE:\s*(.*)", text)
            desc_match = re.search(r"DESC:\s*([\s\S]*?)(?:TAGS:|$)", text)
            tags_match = re.search(r"TAGS:\s*([\s\S]*?)(?:MUSIC:|$)", text)
            music_match = re.search(r"MUSIC:\s*(.*)", text)

            if not (title_match and desc_match and tags_match):
                print(f"⚠️ {model_name} ne format sahi nahi diya, next model try karte hain...")
                continue

            title = title_match.group(1).strip()
            desc = desc_match.group(1).strip()
            tags = tags_match.group(1).strip()
            if music_match:
                music_prompt = music_match.group(1).strip()

            with open("music_prompt.txt", "w", encoding="utf-8") as f:
                f.write(music_prompt)

            print("✅ Viral Metadata successfully generated!")
            print(f"📌 TITLE: {title}")
            print(f"📌 DESC: {desc}")
            print(f"📌 TAGS: {tags}")
            return title, desc, tags
        except Exception as e:
            print(f"⚠️ Model {model_name} failed: {e}")
            time.sleep(1)

    # Agar sab fail ho jaye to bhi ek decent fallback viral-style metadata do (generic nahi)
    with open("music_prompt.txt", "w", encoding="utf-8") as f:
        f.write(music_prompt)
    fallback_title = f"You Won't Believe What Happens Next 😱 | {topic[:40]}"
    fallback_desc = (f"This story about {topic} will hit you right in the feels 💔 Watch till the end!\n"
                      f"#shorts #viral #fyp #trending #story #emotional")
    fallback_tags = f"shorts, viral shorts, trending shorts, fyp, emotional story, viral video, {topic.lower()}"
    return fallback_title, fallback_desc, fallback_tags

def process_stories():
    if not os.path.exists(STORY_FILE):
        print(f"❌ ERROR: {STORY_FILE} file not found!")
        sys.exit(1)
        
    with open(STORY_FILE, "r", encoding="utf-8") as f: content = f.read().strip()
    
    if not content:
        print(f"❌ ERROR: {STORY_FILE} is empty!")
        sys.exit(1)
        
    topics = [t.strip() for t in content.split("\n") if t.strip()]
    parts = topics[0].split("|")
    duration_sec, topic = (int(re.search(r'\d+', parts[0]).group()), parts[1].strip()) if len(parts) > 1 else (30, topics[0])
    
    print(f"📝 Topic: {topic}, Duration: {duration_sec}s")
    
    ai_output = generate_ai_script(duration_sec, topic)
    
    if not ai_output:
        print("❌ CRITICAL ERROR: 10 attempts ke baad bhi AI fail ho gaya. Process stopped.")
        sys.exit(1)
        
    with open(PROMPT_FILE, "w", encoding="utf-8") as f: f.write(ai_output + "\n")
    
    title, desc, tags = generate_ai_metadata(topic)
    with open(METADATA_FILE, "w", encoding="utf-8") as f: f.write(f"TITLE: {title}\nDESC: {desc}\nTAGS: {tags}")
    with open(STORY_FILE, "w", encoding="utf-8") as f: f.write("\n".join(topics[1:]) + "\n" if len(topics) > 1 else "")
    print("🚀 All processes completed successfully!")

if __name__ == "__main__":
    process_stories()
