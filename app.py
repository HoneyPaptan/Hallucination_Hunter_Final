import os
import base64
import streamlit as st
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# -----------------------------
# Gemini Client (Latest API)
# -----------------------------
from google import genai
from google.genai import types

client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

# -----------------------------
# Tavily Updated Client
# -----------------------------
from tavily import TavilyClient

tavily = TavilyClient(api_key=os.environ.get("TAVILY_API_KEY"))

# -----------------------------
# Gemini LLM Processing
# -----------------------------
def ask_gemini(prompt, system_instruction=None, image_data=None):
    print("\n[DEBUG] Sending prompt to Gemini...")
    model = "gemini-2.0-flash-lite"
    
    parts = []
    
    # Add image if provided
    if image_data:
        parts.append(types.Part(inline_data=types.Blob(
            mime_type="image/jpeg",
            data=image_data
        )))
    
    # Add text prompt
    parts.append(types.Part(text=prompt))
    
    contents = [
        types.Content(
            role="user",
            parts=parts,
        ),
    ]
    
    config = types.GenerateContentConfig(
        temperature=0.7,
        max_output_tokens=2048,
        system_instruction=system_instruction if system_instruction else None,
    )
    
    full_response = ""
    print("\n--- GEMINI RAW OUTPUT START ---")
    
    try:
        for chunk in client.models.generate_content_stream(
            model=model,
            contents=contents,
            config=config,
        ):
            if chunk.text:
                print(chunk.text, end="")
                full_response += chunk.text
    except Exception as e:
        print(f"\n[ERROR] Gemini API error: {e}")
        full_response = f"Error generating response: {str(e)}"
    
    print("\n--- GEMINI RAW OUTPUT END ---\n")
    return full_response

# -----------------------------
# Fact Verification with LLM
# -----------------------------
def verify_facts_with_llm(user_claim, web_evidence):
    """Use Gemini to verify if the user's original claim is true or false based on web evidence."""
    
    verification_prompt = f"""You are a strict fact-checker. Your job is to determine if the USER'S ORIGINAL CLAIM is true or false based on web evidence.

USER'S ORIGINAL CLAIM TO VERIFY:
{user_claim}

WEB EVIDENCE FROM TRUSTED SOURCES:
{web_evidence}

CRITICAL INSTRUCTIONS:
1. Focus ONLY on verifying the USER'S ORIGINAL CLAIM above
2. Compare each part of the claim against the web evidence
3. If ANY part of the claim contradicts the evidence, it's a hallucination
4. Score based on how much of the original claim is FALSE or UNSUPPORTED

HALLUCINATION SCORING:
- 0.0 = The claim is completely TRUE and verified by evidence
- 0.2 = Minor inaccuracies or missing context
- 0.4 = Some facts correct, some incorrect
- 0.6 = Mostly incorrect with few correct details
- 0.8 = Largely fabricated or contradicts evidence
- 1.0 = Completely FALSE, directly contradicted by all evidence

Respond EXACTLY in this format:
SCORE: [number between 0.0 and 1.0]
CLAIM_STATUS: [TRUE/PARTIALLY_TRUE/FALSE]
REASONING: [explain why the original claim is true or false]
CORRECT_FACTS: [what is actually true according to evidence]
FALSE_CLAIMS: [what parts of the original claim are false]
CONTRADICTIONS: [direct contradictions between claim and evidence]"""

    verification_result = ask_gemini(
        verification_prompt,
        system_instruction="You are a precise fact-checker verifying the user's original claim. Be strict and objective."
    )
    
    return verification_result

def parse_verification_result(verification_text):
    """Extract score and details from verification response."""
    import re
    
    score_match = re.search(r'SCORE:\s*([0-9.]+)', verification_text)
    score = float(score_match.group(1)) if score_match else 0.5
    
    status_match = re.search(r'CLAIM_STATUS:\s*(\w+)', verification_text)
    status = status_match.group(1) if status_match else "UNKNOWN"
    
    reasoning_match = re.search(r'REASONING:\s*(.+?)(?=CORRECT_FACTS:|$)', verification_text, re.DOTALL)
    reasoning = reasoning_match.group(1).strip() if reasoning_match else "Unable to parse reasoning"
    
    correct_match = re.search(r'CORRECT_FACTS:\s*(.+?)(?=FALSE_CLAIMS:|$)', verification_text, re.DOTALL)
    correct = correct_match.group(1).strip() if correct_match else "None identified"
    
    false_match = re.search(r'FALSE_CLAIMS:\s*(.+?)(?=CONTRADICTIONS:|$)', verification_text, re.DOTALL)
    false_claims = false_match.group(1).strip() if false_match else "None identified"
    
    contradictions_match = re.search(r'CONTRADICTIONS:\s*(.+?)$', verification_text, re.DOTALL)
    contradictions = contradictions_match.group(1).strip() if contradictions_match else "None identified"
    
    return {
        "score": score,
        "status": status,
        "reasoning": reasoning,
        "correct_facts": correct,
        "false_claims": false_claims,
        "contradictions": contradictions
    }

# -----------------------------
# Image Analysis
# -----------------------------
def analyze_image_with_web_verification(image_bytes, user_query=None):
    """Analyze image and verify claims against web evidence."""
    
    # First, get Gemini's description of the image
    image_description_prompt = "Describe what you see in this image in detail. Include any text, objects, people, places, or events shown."
    
    image_description = ask_gemini(image_description_prompt, image_data=image_bytes)
    
    # If user provided a query about the image, verify it
    if user_query:
        verify_prompt = f"""Analyze this image and determine if the following claim about it is true:

CLAIM: {user_query}

Based on what you see in the image, is this claim accurate? Respond with:
VERDICT: [TRUE/FALSE/PARTIALLY_TRUE]
REASONING: [explain your assessment]
IMAGE_SHOWS: [what the image actually shows]"""
        
        verification = ask_gemini(verify_prompt, image_data=image_bytes)
        return image_description, verification
    
    return image_description, None

# -----------------------------
# Tavily Web Search
# -----------------------------
def tavily_search(query):
    print(f"\n[DEBUG] Tavily searching for: {query}\n")
    try:
        result = tavily.search(query=query, max_results=5)
        return result
    except Exception as e:
        print(f"[ERROR] Tavily failure: {e}")
        return {"results": [], "error": str(e)}

# -----------------------------
# Streamlit App
# -----------------------------
st.set_page_config(page_title="Hallucination Hunter", layout="wide")
st.title("🧪 Hallucination Hunter")
st.write("Verify text claims and images using AI-powered fact-checking with real-world web evidence.")

# Create tabs for text and image analysis
tab1, tab2 = st.tabs(["📝 Text Verification", "🖼️ Image Verification"])

# -----------------------------
# TEXT VERIFICATION TAB
# -----------------------------
with tab1:
    st.subheader("Enter a claim to verify")
    user_input = st.text_area("Enter your claim or statement", height=150, 
                               placeholder="Example: Barack Obama was born in Kenya and served as the first African President of the United States.")

    if st.button("Verify Claim", key="verify_text"):
        if not user_input.strip():
            st.warning("Please enter a claim to verify.")
            st.stop()
        
        with st.spinner("Analyzing claim..."):
            # Store the original claim
            original_claim = user_input.strip()
            
            # -----------------------------
            # 1. Search for Evidence
            # -----------------------------
            tavily_data = tavily_search(original_claim)
            
            st.subheader("🌐 Web Evidence")
            
            if tavily_data and "results" in tavily_data and tavily_data["results"]:
                for idx, result in enumerate(tavily_data["results"][:3], 1):
                    with st.expander(f"Source {idx}: {result.get('title', 'Unknown')}"):
                        st.write(f"**URL:** {result.get('url', 'N/A')}")
                        st.write(f"**Content:** {result.get('content', 'N/A')}")
            else:
                st.warning("⚠️ No web evidence found - cannot verify claim")
            
            # -----------------------------
            # 2. Fact Verification
            # -----------------------------
            if tavily_data and "results" in tavily_data and tavily_data["results"]:
                combined_web = "\n\n".join([
                    f"Source: {r.get('title', 'Unknown')}\nURL: {r.get('url', 'N/A')}\nContent: {r.get('content', '')}" 
                    for r in tavily_data["results"]
                ])
            else:
                combined_web = "No web evidence available for comparison."
            
            with st.spinner("Fact-checking with AI..."):
                verification_result = verify_facts_with_llm(original_claim, combined_web)
                parsed_result = parse_verification_result(verification_result)
            
            st.subheader("📊 Verification Results")
            
            hallucination_score = parsed_result["score"]
            claim_status = parsed_result["status"]
            
            # Display status badge
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Hallucination Score", f"{hallucination_score:.2f}")
            with col2:
                if claim_status == "TRUE":
                    st.success(f"✅ {claim_status}")
                elif claim_status == "FALSE":
                    st.error(f"❌ {claim_status}")
                else:
                    st.warning(f"⚠️ {claim_status}")
            
            # Visual indicator
            if hallucination_score < 0.3:
                st.success("✅ Low hallucination risk - Claim appears accurate")
            elif hallucination_score < 0.6:
                st.warning("⚠️ Moderate hallucination risk - Some inaccuracies detected")
            else:
                st.error("❌ High hallucination risk - Claim is largely or completely false")
            
            # Detailed breakdown
            st.markdown("---")
            col_left, col_right = st.columns(2)
            
            with col_left:
                st.markdown("**✓ What's Actually True:**")
                st.info(parsed_result["correct_facts"])
            
            with col_right:
                st.markdown("**✗ False Claims Detected:**")
                st.error(parsed_result["false_claims"])
            
            if parsed_result["contradictions"] and parsed_result["contradictions"] != "None identified":
                st.markdown("**⚠️ Direct Contradictions:**")
                st.warning(parsed_result["contradictions"])
            
            st.markdown("**📝 Analysis:**")
            st.write(parsed_result["reasoning"])
            
            # Debug section
            with st.expander("🛠 Debug Information"):
                st.code(f"""Original Claim:
{original_claim}

Verification Result:
{verification_result}

Parsed Score: {hallucination_score}
Claim Status: {claim_status}
""", language="text")

# -----------------------------
# IMAGE VERIFICATION TAB
# -----------------------------
with tab2:
    st.subheader("Upload an image to analyze")
    uploaded_image = st.file_uploader("Choose an image", type=['png', 'jpg', 'jpeg'])
    image_claim = st.text_input("Optional: Enter a claim about this image to verify", 
                                 placeholder="Example: This image shows the Eiffel Tower in London")
    
    if uploaded_image and st.button("Analyze Image", key="analyze_image"):
        with st.spinner("Analyzing image..."):
            # Display the image
            st.image(uploaded_image, caption="Uploaded Image", use_container_width=True)
            
            # Read image bytes
            image_bytes = uploaded_image.read()
            
            # Analyze the image
            image_description, verification = analyze_image_with_web_verification(
                image_bytes, 
                image_claim if image_claim.strip() else None
            )
            
            st.subheader("🔍 Image Analysis")
            st.write("**What Gemini sees in the image:**")
            st.info(image_description)
            
            # If there's a claim to verify
            if verification and image_claim.strip():
                st.subheader("📊 Claim Verification")
                st.write(f"**Your Claim:** {image_claim}")
                st.write("**Verification Result:**")
                st.write(verification)
                
                # Search web for additional context
                with st.spinner("Searching web for additional verification..."):
                    web_results = tavily_search(image_claim)
                    
                    if web_results and "results" in web_results and web_results["results"]:
                        st.subheader("🌐 Web Evidence")
                        for idx, result in enumerate(web_results["results"][:3], 1):
                            with st.expander(f"Source {idx}: {result.get('title', 'Unknown')}"):
                                st.write(f"**URL:** {result.get('url', 'N/A')}")
                                st.write(f"**Content:** {result.get('content', 'N/A')}")
