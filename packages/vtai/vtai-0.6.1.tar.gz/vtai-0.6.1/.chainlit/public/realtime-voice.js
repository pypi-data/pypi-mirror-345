// realtime-voice.js
// Client-side handler for real-time voice conversation using WebRTC and OpenAI's Realtime API

(function() {
  // Global variables for WebRTC and WebSocket connections
  let mediaRecorder = null;
  let audioContext = null;
  let websocket = null;
  let recording = false;
  let sessionId = null;
  let apiKey = null;
  let websocketUrl = null;
  let currentModel = null;
  let currentVoice = null;
  let language = 'en';

  // Listen for custom events from the server
  document.addEventListener('DOMContentLoaded', function() {
    // Check if window.chainlit is available (it's loaded asynchronously)
    const checkChainlit = setInterval(() => {
      if (window.chainlit) {
        clearInterval(checkChainlit);
        setupEventListeners();
      }
    }, 100);
  });

  function setupEventListeners() {
    // Listen for custom events from the server
    window.chainlit.on('custom', async (data) => {
      // Handle different event types
      if (data.type === 'realtime_init') {
        await initializeRealtimeVoice(data);
      } else if (data.type === 'realtime_terminate') {
        terminateRealtimeVoice(data);
      } else if (data.type === 'realtime_toggle_recording') {
        toggleRecording(data);
      } else if (data.type === 'realtime_set_language') {
        setLanguage(data);
      } else if (data.type === 'realtime_set_voice') {
        setVoice(data);
      }
    });
  }

  async function initializeRealtimeVoice(data) {
    // Store session variables
    sessionId = data.sessionId;
    apiKey = data.apiKey;
    websocketUrl = data.websocketUrl;
    currentModel = data.model;
    currentVoice = data.voice || 'nova';

    console.log(`Initializing real-time voice session: ${sessionId}`);

    try {
      // Request microphone permission
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });

      // Set up audio processing
      setupAudioProcessing(stream);

      // Initialize WebSocket connection (but don't connect yet)
      initializeWebSocket();

      console.log('Real-time voice initialized successfully');
    } catch (error) {
      console.error('Error initializing real-time voice:', error);
      window.chainlit.sendMessage({
        content: `Error initializing real-time voice: ${error.message}. Please check your microphone permissions.`,
      });
    }
  }

  function setupAudioProcessing(stream) {
    // Create an audio context
    audioContext = new (window.AudioContext || window.webkitAudioContext)();

    // Create a media recorder
    const options = { mimeType: 'audio/webm' };
    try {
      mediaRecorder = new MediaRecorder(stream, options);
    } catch (e) {
      console.error('MediaRecorder creation failed:', e);
      // Try fallback options
      try {
        mediaRecorder = new MediaRecorder(stream);
      } catch (e2) {
        console.error('MediaRecorder creation completely failed:', e2);
        window.chainlit.sendMessage({
          content: 'Your browser does not support the necessary audio recording features. Please try a different browser.',
        });
        return;
      }
    }

    // Set up media recorder event handlers
    mediaRecorder.ondataavailable = handleAudioData;
    mediaRecorder.onerror = (event) => {
      console.error('MediaRecorder error:', event);
    };

    console.log('Audio processing setup complete');
  }

  function initializeWebSocket() {
    // This function prepares the WebSocket but doesn't connect yet
    // The actual connection will be established when recording starts
    console.log('WebSocket prepared for connection');
  }

  function connectWebSocket() {
    // Check if we already have an active connection
    if (websocket && websocket.readyState === WebSocket.OPEN) {
      console.log('WebSocket already connected');
      return;
    }

    // Create WebSocket connection to OpenAI
    websocket = new WebSocket(websocketUrl);

    // Configure WebSocket event handlers
    websocket.onopen = () => {
      console.log('WebSocket connection established');

      // Send initial configuration message
      const configMessage = {
        action: 'conversation.item.create',
        model: currentModel,
        options: {
          voice: currentVoice,
          language: language,
        },
      };

      websocket.send(JSON.stringify(configMessage));
    };

    websocket.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);

        // Handle different message types from the server
        if (data.type === 'text') {
          // Display the text response
          window.chainlit.sendMessage({
            content: data.text,
          });
        } else if (data.type === 'audio') {
          // Play the audio response
          playAudioResponse(data.audio);
        } else if (data.type === 'error') {
          console.error('Error from OpenAI:', data.error);
          window.chainlit.sendMessage({
            content: `Error from OpenAI: ${data.error}`,
          });
        }
      } catch (error) {
        console.error('Error processing WebSocket message:', error);
      }
    };

    websocket.onerror = (error) => {
      console.error('WebSocket error:', error);
      window.chainlit.sendMessage({
        content: 'Error with real-time voice connection. Please try again.',
      });
    };

    websocket.onclose = () => {
      console.log('WebSocket connection closed');
    };
  }

  function terminateRealtimeVoice(data) {
    // Verify this is for our session
    if (data.sessionId !== sessionId) {
      return;
    }

    // Stop recording if active
    if (recording && mediaRecorder) {
      mediaRecorder.stop();
      recording = false;
    }

    // Close WebSocket if open
    if (websocket) {
      websocket.close();
      websocket = null;
    }

    // Release audio resources
    if (audioContext) {
      audioContext.close();
      audioContext = null;
    }

    // Clear session variables
    sessionId = null;
    apiKey = null;
    mediaRecorder = null;

    console.log('Real-time voice session terminated');
  }

  function toggleRecording(data) {
    // Verify this is for our session
    if (data.sessionId !== sessionId) {
      return;
    }

    if (!mediaRecorder) {
      console.error('MediaRecorder not initialized');
      window.chainlit.sendMessage({
        content: 'Error: Audio recording not initialized. Please refresh the page and try again.',
      });
      return;
    }

    // Toggle recording state
    if (data.active) {
      startRecording();
    } else {
      stopRecording();
    }
  }

  function startRecording() {
    if (!recording) {
      // Ensure WebSocket is connected
      connectWebSocket();

      // Start recording
      try {
        mediaRecorder.start(100); // Send data every 100ms
        recording = true;
        console.log('Recording started');
      } catch (error) {
        console.error('Error starting recording:', error);
        window.chainlit.sendMessage({
          content: `Error starting recording: ${error.message}`,
        });
      }
    }
  }

  function stopRecording() {
    if (recording) {
      // Stop recording
      try {
        mediaRecorder.stop();
        recording = false;
        console.log('Recording stopped');
      } catch (error) {
        console.error('Error stopping recording:', error);
      }
    }
  }

  function handleAudioData(event) {
    // Process audio data when available
    if (event.data.size > 0 && websocket && websocket.readyState === WebSocket.OPEN) {
      // Convert to binary data
      const reader = new FileReader();
      reader.onload = () => {
        // Send audio data to WebSocket
        const audioData = reader.result;

        // Create a message with the audio data
        const message = {
          action: 'conversation.item.update',
          data: {
            type: 'audio',
            audio: btoa(String.fromCharCode.apply(null, new Uint8Array(audioData))),
          },
        };

        websocket.send(JSON.stringify(message));
      };

      reader.readAsArrayBuffer(event.data);
    }
  }

  function playAudioResponse(base64Audio) {
    // Convert base64 audio to ArrayBuffer
    const binaryString = window.atob(base64Audio);
    const len = binaryString.length;
    const bytes = new Uint8Array(len);

    for (let i = 0; i < len; i++) {
      bytes[i] = binaryString.charCodeAt(i);
    }

    // Create an audio element and play the response
    const audioBlob = new Blob([bytes], { type: 'audio/mp3' });
    const audioUrl = URL.createObjectURL(audioBlob);
    const audio = new Audio(audioUrl);

    audio.onended = () => {
      URL.revokeObjectURL(audioUrl);
    };

    audio.play().catch(error => {
      console.error('Error playing audio:', error);
    });
  }

  function setLanguage(data) {
    // Verify this is for our session
    if (data.sessionId !== sessionId) {
      return;
    }

    // Update language
    language = data.language;
    console.log(`Language set to: ${language}`);

    // If WebSocket is connected, send language update
    if (websocket && websocket.readyState === WebSocket.OPEN) {
      const message = {
        action: 'conversation.update',
        options: {
          language: language,
        },
      };

      websocket.send(JSON.stringify(message));
    }
  }

  function setVoice(data) {
    // Verify this is for our session
    if (data.sessionId !== sessionId) {
      return;
    }

    // Update voice
    currentVoice = data.voice;
    console.log(`Voice set to: ${currentVoice}`);

    // If WebSocket is connected, send voice update
    if (websocket && websocket.readyState === WebSocket.OPEN) {
      const message = {
        action: 'conversation.update',
        options: {
          voice: currentVoice,
        },
      };

      websocket.send(JSON.stringify(message));
    }
  }
})();