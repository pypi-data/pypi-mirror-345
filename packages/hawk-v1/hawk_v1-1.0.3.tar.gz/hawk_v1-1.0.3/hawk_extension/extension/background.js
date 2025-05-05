// H.A.W.K - High-Accuracy Wordsmithing Kernel
// Local TensorFlow.js Implementation

// Load TensorFlow.js and model when extension loads
let model = null;
let tokenizer = null;
let modelLoaded = false;
let loadingPromise = null;

// Initialize model loading
async function initializeModel() {
  if (loadingPromise) return loadingPromise;
  
  loadingPromise = new Promise(async (resolve) => {
    try {
      console.log('Loading TensorFlow.js...');
      // Load tokenizer from extension's resources
      tokenizer = await fetch(chrome.runtime.getURL('model/tokenizer.json'))
        .then(response => response.json());
      
      // Load the model
      console.log('Loading model...');
      model = await tf.loadLayersModel(chrome.runtime.getURL('model/model.json'));
      
      console.log('Model loaded successfully');
      modelLoaded = true;
      resolve(true);
    } catch (error) {
      console.error('Error loading model:', error);
      // Fallback to rule-based enhancement if model fails to load
      modelLoaded = false;
      resolve(false);
    }
  });
  
  return loadingPromise;
}

// Start loading the model as soon as the extension loads
initializeModel();

// Listen for messages from popup
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'enhancePrompt') {
    enhancePrompt(request.prompt, request.style || 'general')
      .then(enhancedPrompt => {
        sendResponse({ enhancedPrompt });
      })
      .catch(error => {
        console.error('Error details:', error);
        sendResponse({ error: error.message });
      });
    return true; // Will respond asynchronously
  }
});

// Main function to enhance prompts
async function enhancePrompt(prompt, style) {
  try {
    console.log('Enhancing prompt with style:', style);
    
    // Make sure the model is loaded
    const isModelReady = await initializeModel();
    
    if (isModelReady && modelLoaded) {
      return await enhanceWithModel(prompt, style);
    } else {
      // Fallback to rule-based enhancement
      return enhanceWithRules(prompt, style);
    }
  } catch (error) {
    console.error('Enhancement error:', error);
    // Always have a fallback
    return enhanceWithRules(prompt, style);
  }
}

// Rule-based enhancement as fallback
function enhanceWithRules(prompt, style) {
  // Templates for different styles
  const templates = {
    code: `I need code that accomplishes the following task:
${prompt}

Please provide a solution with:
- Clear, well-documented code
- Error handling
- Efficient implementation
- Explanation of the approach`,

    creative: `I'm looking for creative writing on the following topic:
${prompt}

Please make it:
- Engaging and vivid
- With interesting characters and settings
- Appropriate pacing and structure
- Original and thought-provoking`,

    technical: `I need technical information about:
${prompt}

Please include:
- Detailed technical specifications
- Key concepts and principles
- Practical applications
- Latest developments in this field`,

    academic: `I'm researching the following academic subject:
${prompt}

Please provide:
- Scholarly analysis
- Key theories and frameworks
- References to important research
- Counterarguments and limitations`,

    general: `I'd like comprehensive information about:
${prompt}

Please provide:
- Clear explanation with important details
- Different perspectives or approaches
- Practical examples or applications
- Key considerations and nuances`
  };

  // Choose template based on style or default to general
  const template = templates[style] || templates.general;
  
  // Add some dynamic elements based on prompt content
  let enhancedPrompt = template;
  
  // Check for code-related keywords
  if (prompt.toLowerCase().includes('code') || 
      prompt.toLowerCase().includes('function') ||
      prompt.toLowerCase().includes('program') ||
      prompt.toLowerCase().includes('algorithm')) {
    enhancedPrompt += "\n\nIf providing code examples, please ensure they are runnable and include comments.";
  }
  
  // Check for comparison keywords
  if (prompt.toLowerCase().includes('compare') || 
      prompt.toLowerCase().includes('versus') || 
      prompt.toLowerCase().includes('vs')) {
    enhancedPrompt += "\n\nWhen making comparisons, please provide a balanced assessment with clear criteria.";
  }
  
  // Add a polite closing
  enhancedPrompt += "\n\nThank you for providing a thorough response.";
  
  return enhancedPrompt;
}

// Model-based enhancement (when TensorFlow model is available)
async function enhanceWithModel(prompt, style) {
  try {
    // Prepare the prompt for the model with style guidance
    let stylePrompt = "";
    switch (style) {
      case 'code':
        stylePrompt = "Enhance this prompt for coding: ";
        break;
      case 'creative':
        stylePrompt = "Enhance this prompt for creative writing: ";
        break;
      case 'technical':
        stylePrompt = "Enhance this prompt for technical documentation: ";
        break;
      case 'academic':
        stylePrompt = "Enhance this prompt for academic research: ";
        break;
      default:
        stylePrompt = "Enhance this prompt: ";
    }
    
    // Very simplified tokenization (would use the actual tokenizer in production)
    const input = stylePrompt + prompt;
    const tokens = simplifiedTokenize(input);
    
    // Get prediction from model
    const prediction = await runInference(tokens);
    
    // Very simplified detokenization (placeholder for actual implementation)
    let enhancedPrompt = simplifiedDetokenize(prediction);
    
    // Fallback if the model output is problematic
    if (!enhancedPrompt || enhancedPrompt.length < prompt.length) {
      return enhanceWithRules(prompt, style);
    }
    
    return enhancedPrompt;
  } catch (error) {
    console.error('Model inference error:', error);
    // Fallback to rule-based
    return enhanceWithRules(prompt, style);
  }
}

// Simplified tokenization (placeholder for actual implementation)
function simplifiedTokenize(text) {
  // In a real implementation, this would use the tokenizer
  // For now, just return a dummy tensor
  return tf.tensor2d([Array(512).fill(0)]);
}

// Simplified detokenization (placeholder for actual implementation)
function simplifiedDetokenize(prediction) {
  // In a real implementation, this would convert model output to text
  // For now, return to rule-based enhancement
  return null;
}

// Run model inference (placeholder for actual implementation)
async function runInference(tokens) {
  // In a real implementation, this would run the model
  // For now, return null to trigger the fallback
  return null;
} 