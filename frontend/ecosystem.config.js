module.exports = {
  apps: [
    {
      name: "realestate-frontend",
      script: "node_modules/.bin/next",
      args: "start -p 3008",
      cwd: "/root/realestate-ai/frontend",
      env: {
        NODE_ENV: "production",
      },
    },
  ],
};
