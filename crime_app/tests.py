{% extends "crime_app/officerPage/main.html" %}
{% load static %}
{% load crispy_forms_tags %}
{% block content %}
<div class="bg-white p-6 rounded-2xl shadow-md border border-gray-200 space-y-6">

    <!-- Header -->
    <div class="flex items-center justify-between border-b pb-3">
        <h2 class="text-xl font-semibold text-gray-800">Quick Report Submission</h2>
        <div class="space-x-2">
            <button id="showFormBtn" class="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg font-semibold transition">
                📝 New Report
            </button>
            <button id="showTableBtn" class="bg-gray-200 hover:bg-gray-300 text-gray-800 px-4 py-2 rounded-lg font-semibold transition">
                📄 View Reports
            </button>
        </div>
    </div>

    <!-- Report Form -->
    <div id="reportFormSection" class="space-y-6">
        <h3 class="text-lg font-semibold text-gray-700 border-b pb-2">Incident Report Form</h3>

        <form method="POST" enctype="multipart/form-data" class="space-y-6" id="reportSubmissionForm" action="{% url 'add-report' %}">
            {% csrf_token %}
            {{ form|crispy }}

            <div class="border border-gray-200 rounded-2xl p-6 bg-gray-50 space-y-6 shadow-sm">
                <h4 class="flex items-center gap-2 text-lg font-semibold text-gray-800 border-b pb-2">
                    <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5 text-yellow-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 10l4.553 2.276A2 2 0 0120 14v4a2 2 0 01-2 2H6a2 2 0 01-2-2v-4a2 2 0 01.447-1.276L9 10m6 0V6a2 2 0 00-2-2H8a2 2 0 00-2 2v4" />
                    </svg>
                    Multimedia Evidence
                </h4>

                <div class="grid md:grid-cols-2 gap-6">

                    <!-- Photo Capture -->
                    <div class="border-2 border-dashed rounded-xl p-6 flex flex-col items-center justify-center text-center bg-white hover:bg-gray-50 transition">
                        <svg xmlns="http://www.w3.org/2000/svg" class="w-10 h-10 text-gray-400 mb-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4-4m0 0l4 4m-4-4v12M12 4l4 4m0 0l4-4m-4 4v12" />
                        </svg>
                        <h5 class="font-semibold text-gray-700">Take Photos</h5>
                        <p class="text-sm text-gray-500 mb-4">Capture photos using your device camera</p>
                        <button type="button" id="startCamera" class="bg-orange-500 hover:bg-orange-600 text-white px-4 py-2 rounded-lg font-medium transition">
                            + Open Camera
                        </button>
                        <video id="camera" autoplay class="rounded-lg border w-full max-h-64 mt-4 hidden"></video>
                        <canvas id="snapshot" class="hidden rounded-lg border w-full max-h-64 mt-4"></canvas>
                        <button type="button" id="capturePhoto" class="bg-yellow-500 text-white px-4 py-2 rounded-lg mt-2 hidden">📷 Capture</button>
                    </div>

                    <!-- Video Recording -->
                    <div class="border-2 border-dashed rounded-xl p-6 flex flex-col items-center justify-center text-center bg-white hover:bg-gray-50 transition">
                        <svg xmlns="http://www.w3.org/2000/svg" class="w-10 h-10 text-gray-400 mb-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 10l4.553 2.276A2 2 0 0120 14v4a2 2 0 01-2 2H6a2 2 0 01-2-2v-4a2 2 0 01.447-1.276L9 10m6 0V6a2 2 0 00-2-2H8a2 2 0 00-2 2v4" />
                        </svg>
                        <h5 class="font-semibold text-gray-700">Record Video</h5>
                        <p class="text-sm text-gray-500 mb-4">Record video evidence of the incident</p>

                        <video id="videoPreview" autoplay class="rounded-lg border w-full max-h-64 mt-4 hidden"></video>

                        <div class="flex space-x-3 mt-4">
                            <button type="button" id="startVideo" class="bg-orange-500 hover:bg-orange-600 text-white px-4 py-2 rounded-lg font-medium transition">
                                🎥 Start Recording
                            </button>
                            <button type="button" id="stopVideo" class="bg-gray-300 text-gray-700 px-4 py-2 rounded-lg font-medium transition hidden">
                                ⏹ Stop
                            </button>
                        </div>
                    </div>
                </div>

                <!-- Audio Recording -->
                <div class="border-l-4 border-orange-400 bg-orange-50 rounded-xl p-4 flex items-center justify-between">
                    <div>
                        <h5 class="font-semibold text-orange-700 flex items-center gap-2">
                            <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
                            </svg>
                            Voice Note
                        </h5>
                        <p class="text-sm text-orange-600">Record audio description of the incident</p>
                    </div>
                    <div class="flex items-center gap-3">
                        <span id="timer" class="text-orange-700 font-semibold text-lg">00:00</span>
                        <button type="button" id="startRecord" class="bg-orange-500 hover:bg-orange-600 text-white px-4 py-2 rounded-lg font-medium transition">
                            🎙 Record
                        </button>
                        <button type="button" id="stopRecord" class="bg-gray-300 text-gray-700 px-4 py-2 rounded-lg font-medium transition hidden">
                            ⏹ Stop
                        </button>
                    </div>
                </div>
                <audio id="audioPreview" controls class="hidden w-full mt-2"></audio>

                <!-- File Upload -->
                <div class="border-2 border-dashed rounded-xl p-6 text-center bg-white hover:bg-gray-50 transition">
                    <svg xmlns="http://www.w3.org/2000/svg" class="w-10 h-10 text-gray-400 mx-auto mb-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4-4m0 0l4 4m-4-4v12M12 4l4 4m0 0l4-4m-4 4v12" />
                    </svg>
                    <h5 class="font-semibold text-gray-700">Upload Files</h5>
                    <p class="text-sm text-gray-500 mb-4">Upload photos, videos, or documents from your device</p>
                    <input type="file" name="evidence_files" multiple class="hidden" id="fileUpload">
                    <label for="fileUpload" class="cursor-pointer bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg font-medium inline-block">+ Choose Files</label>
                    <p class="text-xs text-gray-400 mt-2">Supported: JPG, PNG, MP4, PDF, DOC (Max 10MB per file)</p>
                </div>
            </div>

            <div class="text-right">
                <button type="submit" id="submitButton"
                    class="bg-yellow-500 hover:bg-yellow-600 text-white px-6 py-2 rounded-lg font-semibold transition">
                    ✅ Submit Report
                </button>
            </div>
        </form>
    </div>

    <!-- Table -->
   
<div class="mt-8 bg-white rounded-2xl shadow-md overflow-hidden border border-gray-200">
  <table class="w-full text-left border-collapse">
    <thead>
      <tr class="bg-gray-100 text-gray-700 uppercase text-sm">
        <th class="p-3 border-b">#</th>
        <th class="p-3 border-b">Report ID</th>
        <th class="p-3 border-b">Title</th>
        <th class="p-3 border-b">Incident Type</th>
        <th class="p-3 border-b">Department</th>
        <th class="p-3 border-b">Reporter</th>
        <th class="p-3 border-b">Status</th>
        <th class="p-3 border-b">Date Reported</th>
        <th class="p-3 border-b text-center">Action</th>
      </tr>
    </thead>

    <tbody>
      {% for report in reports %}
      <tr class="border-b hover:bg-gray-50 text-gray-700">
        <td class="p-3">{{ forloop.counter }}</td>
        <td class="p-3 font-semibold text-gray-800">{{ report.report_id }}</td>
        <td class="p-3">{{ report.title }}</td>
        <td class="p-3">{{ report.incident_type|default:"—" }}</td>
        <td class="p-3">{{ report.department.name|default:"—" }}</td>
        <td class="p-3">
          {% if report.reporter %}
            {{ report.reporter.get_full_name|default:report.reporter.username }}
          {% else %}
            <span class="text-gray-400 italic">Anonymous</span>
          {% endif %}
        </td>

        <td class="p-3">
          {% if report.status == 'Pending' %}
            <span class="px-2 py-1 bg-yellow-100 text-yellow-700 rounded-full text-xs font-medium">Pending</span>
          {% elif report.status == 'Investigating' %}
            <span class="px-2 py-1 bg-blue-100 text-blue-700 rounded-full text-xs font-medium">Investigating</span>
          {% elif report.status == 'Resolved' %}
            <span class="px-2 py-1 bg-green-100 text-green-700 rounded-full text-xs font-medium">Resolved</span>
          {% endif %}
        </td>

        <td class="p-3">{{ report.date_reported|date:"M d, Y - h:i A" }}</td>
        
        <td class="p-3 text-center">
          <a href="" 
             class="text-blue-600 hover:underline hover:text-blue-800 font-medium">
            View
          </a>
        </td>
      </tr>
      {% empty %}
      <tr>
        <td colspan="9" class="text-center text-gray-500 p-6">No reports have been submitted yet.</td>
      </tr>
      {% endfor %}
    </tbody>
  </table>
</div>

</div>

<script>
    let capturedPhotoBlob = null;
    let recordedAudioBlob = null;
    let recordedVideoBlob = null;
    let cameraStream = null;

    // Toggle
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

    // Photo Capture
    const video = document.getElementById('camera');
    const canvas = document.getElementById('snapshot');
    const startCameraBtn = document.getElementById('startCamera');
    const capturePhotoBtn = document.getElementById('capturePhoto');

    startCameraBtn.addEventListener('click', async () => {
        try {
            cameraStream = await navigator.mediaDevices.getUserMedia({ video: true });
            video.srcObject = cameraStream;
            video.classList.remove('hidden');
            capturePhotoBtn.classList.remove('hidden');
        } catch (err) {
            alert("Could not access camera.");
        }
    });
    capturePhotoBtn.addEventListener('click', () => {
        const ctx = canvas.getContext('2d');
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        ctx.drawImage(video, 0, 0);
        canvas.classList.remove('hidden');
        canvas.toBlob(blob => capturedPhotoBlob = blob, 'image/jpeg');
        if (cameraStream) cameraStream.getTracks().forEach(track => track.stop());
        video.classList.add('hidden');
        capturePhotoBtn.classList.add('hidden');
    });

    // Audio Recording
    let mediaRecorder, audioChunks = [], seconds = 0, timerInterval, audioStream = null;
    const startRecordBtn = document.getElementById('startRecord');
    const stopRecordBtn = document.getElementById('stopRecord');
    const audioPreview = document.getElementById('audioPreview');
    const timer = document.getElementById('timer');

    startRecordBtn.addEventListener('click', async () => {
        try {
            audioStream = await navigator.mediaDevices.getUserMedia({ audio: true });
            mediaRecorder = new MediaRecorder(audioStream, { mimeType: 'audio/webm' });
            audioChunks = [];
            mediaRecorder.ondataavailable = e => audioChunks.push(e.data);
            mediaRecorder.onstop = () => {
                recordedAudioBlob = new Blob(audioChunks, { type: 'audio/webm' });
                audioPreview.src = URL.createObjectURL(recordedAudioBlob);
                audioPreview.classList.remove('hidden');
            };
            mediaRecorder.start();
            startRecordBtn.classList.add('hidden');
            stopRecordBtn.classList.remove('hidden');
            timerInterval = setInterval(() => {
                seconds++;
                timer.textContent = new Date(seconds * 1000).toISOString().substr(14, 5);
            }, 1000);
        } catch (err) {
            alert("Could not access microphone.");
        }
    });
    stopRecordBtn.addEventListener('click', () => {
        mediaRecorder.stop();
        clearInterval(timerInterval);
        startRecordBtn.classList.remove('hidden');
        stopRecordBtn.classList.add('hidden');
        timer.textContent = '00:00';
    });

    // Video Recording
    let videoRecorder, videoChunks = [], videoStream = null;
    const startVideoBtn = document.getElementById('startVideo');
    const stopVideoBtn = document.getElementById('stopVideo');
    const videoPreview = document.getElementById('videoPreview');

    startVideoBtn.addEventListener('click', async () => {
        try {
            videoStream = await navigator.mediaDevices.getUserMedia({ video: true, audio: true });
            videoPreview.srcObject = videoStream;
            videoPreview.classList.remove('hidden');
            videoPreview.controls = false;
            videoChunks = [];

            videoRecorder = new MediaRecorder(videoStream, { mimeType: 'video/webm' });
            videoRecorder.ondataavailable = e => videoChunks.push(e.data);

            videoRecorder.onstop = () => {
                recordedVideoBlob = new Blob(videoChunks, { type: 'video/webm' });

                // Stop the camera stream
                if (videoStream) videoStream.getTracks().forEach(track => track.stop());

                // Show recorded video preview (like audio preview)
                const videoURL = URL.createObjectURL(recordedVideoBlob);
                videoPreview.srcObject = null;
                videoPreview.src = videoURL;
                videoPreview.controls = true;
                videoPreview.classList.remove('hidden');
                videoPreview.play();
            };

            videoRecorder.start();
            startVideoBtn.classList.add('hidden');
            stopVideoBtn.classList.remove('hidden');
        } catch (err) {
            alert("Could not access camera or microphone.");
        }
    });

    stopVideoBtn.addEventListener('click', () => {
        if (videoRecorder && videoRecorder.state !== 'inactive') videoRecorder.stop();
        startVideoBtn.classList.remove('hidden');
        stopVideoBtn.classList.add('hidden');
    });



    // Submit
    const form = document.getElementById('reportSubmissionForm');
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    const submitButton = document.getElementById('submitButton');

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const formData = new FormData(form);
        if (capturedPhotoBlob) formData.append('photo_file', capturedPhotoBlob, 'photo.jpg');
        if (recordedAudioBlob) formData.append('audio_file', recordedAudioBlob, 'audio.webm');
        if (recordedVideoBlob) formData.append('video_file', recordedVideoBlob, 'video.webm');
        submitButton.textContent = 'Submitting...';
        submitButton.disabled = true;
        try {
            const response = await fetch(form.action, { method: 'POST', headers: { 'X-CSRFToken': csrfToken }, body: formData });
            if (response.ok) {
                alert('Report submitted successfully!');
                window.location.reload();
            } else alert('Failed to submit report.');
        } catch (error) {
            alert('Network error during submission.');
        } finally {
            submitButton.textContent = '✅ Submit Report';
            submitButton.disabled = false;
        }
    });
</script>
{% endblock %}
