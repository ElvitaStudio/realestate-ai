module.exports = {
  apps: [
    {
      name: "realestate-backend",
      script: "venv/bin/uvicorn",
      args: "app.main:app --host 0.0.0.0 --port 8008",
      cwd: "/root/realestate-ai/backend",
      interpreter: "none",
      env: {
        PYTHONPATH: "/root/realestate-ai/backend",
      },
    },
  ],
};
