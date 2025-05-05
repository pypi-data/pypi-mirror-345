document.addEventListener('DOMContentLoaded', function() {
  const promptInput = document.getElementById('promptInput');
  const enhancedPrompt = document.getElementById('enhancedPrompt');
  const refineButton = document.getElementById('refineButton');
  const copyButton = document.getElementById('copyButton');
  const status = document.getElementById('status');
  const statusText = document.getElementById('statusText');
  const loadingSpinner = document.getElementById('loadingSpinner');
  const styleSelector = document.getElementById('styleSelector');

  // Function to show/hide loading spinner
  function setLoading(isLoading, message = '') {
    if (isLoading) {
      loadingSpinner.style.display = 'block';
    } else {
      loadingSpinner.style.display = 'none';
    }
    statusText.textContent = message;
  }

  // Load saved prompt and style if they exist
  chrome.storage.local.get(['lastPrompt', 'lastStyle'], function(result) {
    if (result.lastPrompt) {
      promptInput.value = result.lastPrompt;
    }
    if (result.lastStyle && styleSelector) {
      styleSelector.value = result.lastStyle;
    }
  });

  refineButton.addEventListener('click', async function() {
    const prompt = promptInput.value.trim();
    if (!prompt) {
      setLoading(false, 'Please enter a prompt first');
      return;
    }

    // Get selected style (default to 'general' if not found)
    const selectedStyle = styleSelector ? styleSelector.value : 'general';

    setLoading(true, 'Enhancing prompt...');
    refineButton.disabled = true;

    try {
      const response = await chrome.runtime.sendMessage({
        action: 'enhancePrompt',
        prompt: prompt,
        style: selectedStyle
      });

      if (response.error) {
        setLoading(false, 'Error: ' + response.error);
        return;
      }

      enhancedPrompt.value = response.enhancedPrompt;
      setLoading(false, 'Prompt enhanced successfully!');
      
      // Save the prompt and style
      chrome.storage.local.set({ 
        lastPrompt: prompt,
        lastStyle: selectedStyle
      });
    } catch (error) {
      setLoading(false, 'Error: Failed to enhance prompt');
    } finally {
      refineButton.disabled = false;
    }
  });

  copyButton.addEventListener('click', function() {
    if (!enhancedPrompt.value) {
      setLoading(false, 'Generate an enhanced prompt first');
      return;
    }

    enhancedPrompt.select();
    document.execCommand('copy');
    setLoading(false, 'Copied to clipboard!');
    
    // Reset message after 2 seconds
    setTimeout(() => {
      if (statusText.textContent === 'Copied to clipboard!') {
        statusText.textContent = '';
      }
    }, 2000);
  });

  // Allow pressing Enter in the input field to trigger enhancement
  promptInput.addEventListener('keydown', function(event) {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      refineButton.click();
    }
  });
}); 