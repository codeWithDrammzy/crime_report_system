<!-- ===================== Report Form Section ===================== -->
<div id="reportFormSection" class="hidden min-h-[80vh] flex flex-col justify-center items-center bg-gray-50 p-10">
  <div class="w-full max-w-3xl bg-white p-8 rounded-2xl shadow-md border border-gray-200">
    <h2 class="text-2xl font-bold text-gray-800 mb-6 text-center">📝 Submit New Crime Report</h2>

    <form method="POST" enctype="multipart/form-data" class="space-y-5">
      {% csrf_token %}
      {{ form|crispy }}

      <!-- ===================== Media Capture Section ===================== -->
      <div class="space-y-6 border-t pt-4">

        <!-- Camera Capture -->
        <div class="text-center">
          <h3 class="font-semibold text-gray-800 mb-2">📸 Take Photo</h3>
          <video id="cameraVideo" autoplay class="w-full rounded-md hidden"></video>
          <canvas id="photoCanvas" class="hidden w-full mt-3 border rounded-md"></canvas>
          <input type="hidden" name="photo_data" id="photoData">
          <div class="space-x-2 mt-3">
            <button type="button" id="startCamera" class="bg-green-600 hover:bg-green-700 text-white px-3 py-1 rounded-lg">Start Camera</button>
            <button type="button" id="capturePhoto" class="bg-yellow-500 hover:bg-yellow-600 text-white px-3 py-1 rounded-lg hidden">Capture Photo</button>
          </div>
        </div>

        <!-- Audio Recorder -->
        <div class="text-center">
          <h3 class="font-semibold text-gray-800 mb-2">🎙️ Record Audio</h3>
          <p id="audioTimer" class="text-gray-600 mb-2">00:00</p>
          <audio id="audioPreview" controls class="hidden w-full mb-2"></audio>
          <input type="hidden" name="audio_data" id="audioData">
          <div class="space-x-2">
            <button type="button" id="startAudio" class="bg-blue-600 hover:bg-blue-700 text-white px-3 py-1 rounded-lg">Start</button>
            <button type="button" id="stopAudio" class="bg-red-600 hover:bg-red-700 text-white px-3 py-1 rounded-lg hidden">Stop</button>
          </div>
        </div>

        <!-- Video Recorder -->
        <div class="text-center">
          <h3 class="font-semibold text-gray-800 mb-2">🎥 Record Video</h3>
          <video id="videoPreview" controls class="w-full rounded-md mb-2 hidden"></video>
          <input type="hidden" name="video_data" id="videoData">
          <div class="space-x-2 mt-2">
            <button type="button" id="startVideo" class="bg-purple-600 hover:bg-purple-700 text-white px-3 py-1 rounded-lg">Start Recording</button>
            <button type="button" id="stopVideo" class="bg-pink-600 hover:bg-pink-700 text-white px-3 py-1 rounded-lg hidden">Stop Recording</button>
          </div>
        </div>

      </div>

      <!-- Submit / Cancel -->
      <div class="flex justify-center space-x-4 mt-8">
        <button type="submit" class="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-lg shadow transition">
          Submit Report
        </button>
        <button type="button" id="cancelFormBtn" class="bg-gray-200 hover:bg-gray-300 text-gray-800 px-6 py-2 rounded-lg shadow transition">
          Cancel
        </button>
      </div>
    </form>
  </div>
</div>

<script>
  // ===================== Toggle Form/Table =====================
  const formSection = document.getElementById('reportFormSection');
  const tableSection = document.getElementById('reportTableSection');
  document.getElementById('showFormBtn').onclick = () => {
    formSection.classList.remove('hidden');
    tableSection.classList.add('hidden');
  };
  document.getElementById('showTableBtn').onclick = () => {
    formSection.classList.add('hidden');
    tableSection.classList.remove('hidden');
  };
  document.getElementById('cancelFormBtn').onclick = () => {
    formSection.classList.add('hidden');
    tableSection.classList.remove('hidden');
  };

  // ===================== Photo Capture =====================
  const video = document.getElementById('cameraVideo');
  const canvas = document.getElementById('photoCanvas');
  const startCamera = document.getElementById('startCamera');
  const capturePhoto = document.getElementById('capturePhoto');
  const photoDataInput = document.getElementById('photoData');
  let photoStream;

  startCamera.addEventListener('click', async () => {
    photoStream = await navigator.mediaDevices.getUserMedia({ video: true });
    video.srcObject = photoStream;
    video.classList.remove('hidden');
    capturePhoto.classList.remove('hidden');
  });

  capturePhoto.addEventListener('click', () => {
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    const ctx = canvas.getContext('2d');
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
    canvas.classList.remove('hidden');
    video.classList.add('hidden');
    capturePhoto.classList.add('hidden');
    // save photo as base64
    photoDataInput.value = canvas.toDataURL('image/png');
    // stop camera
    photoStream.getTracks().forEach(track => track.stop());
  });

  // ===================== Audio Recording =====================
  let audioRecorder, audioChunks = [], audioSeconds = 0, audioTimerInterval;
  const startAudio = document.getElementById('startAudio');
  const stopAudio = document.getElementById('stopAudio');
  const audioPreview = document.getElementById('audioPreview');
  const audioDataInput = document.getElementById('audioData');
  const audioTimer = document.getElementById('audioTimer');

  startAudio.addEventListener('click', async () => {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    audioRecorder = new MediaRecorder(stream);
    audioChunks = [];

    audioRecorder.ondataavailable = e => audioChunks.push(e.data);
    audioRecorder.onstop = () => {
      const audioBlob = new Blob(audioChunks, { type: 'audio/mp3' });
      audioPreview.src = URL.createObjectURL(audioBlob);
      audioPreview.classList.remove('hidden');
      // convert to base64
      const reader = new FileReader();
      reader.onloadend = () => audioDataInput.value = reader.result;
      reader.readAsDataURL(audioBlob);
    };

    audioRecorder.start();
    startAudio.classList.add('hidden');
    stopAudio.classList.remove('hidden');
    audioSeconds = 0;
    audioTimerInterval = setInterval(() => {
      audioSeconds++;
      audioTimer.textContent = new Date(audioSeconds * 1000).toISOString().substr(14, 5);
    }, 1000);
  });

  stopAudio.addEventListener('click', () => {
    audioRecorder.stop();
    clearInterval(audioTimerInterval);
    startAudio.classList.remove('hidden');
    stopAudio.classList.add('hidden');
  });

  // ===================== Video Recording =====================
  let videoRecorder, videoChunks = [];
  const startVideo = document.getElementById('startVideo');
  const stopVideo = document.getElementById('stopVideo');
  const videoPreview = document.getElementById('videoPreview');
  const videoDataInput = document.getElementById('videoData');
  let videoStream;

  startVideo.addEventListener('click', async () => {
    videoStream = await navigator.mediaDevices.getUserMedia({ video: true, audio: true });
    videoRecorder = new MediaRecorder(videoStream);
    videoChunks = [];

    videoRecorder.ondataavailable = e => videoChunks.push(e.data);
    videoRecorder.onstop = () => {
      const videoBlob = new Blob(videoChunks, { type: 'video/webm' });
      videoPreview.src = URL.createObjectURL(videoBlob);
      videoPreview.classList.remove('hidden');
      const reader = new FileReader();
      reader.onloadend = () => videoDataInput.value = reader.result;
      reader.readAsDataURL(videoBlob);
    };

    videoRecorder.start();
    startVideo.classList.add('hidden');
    stopVideo.classList.remove('hidden');
  });

  stopVideo.addEventListener('click', () => {
    videoRecorder.stop();
    stopVideo.classList.add('hidden');
    startVideo.classList.remove('hidden');
    videoStream.getTracks().forEach(track => track.stop());
  });
</script>
