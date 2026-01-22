// Place this file BEFORE including config.js in your HTML when hosting statically (S3/CloudFront)
// Copy to config.override.js and set your backend API base URL (no trailing slash)
// Example include order:
// <script src="/common/config.override.js"></script>
// <script src="/common/config.js"></script>

window.APP_CONFIG = {
  // Point to your deployed backend (e.g., Railway, EB, App Runner)
  API_BASE_URL: "https://your-backend.example.com"
};
