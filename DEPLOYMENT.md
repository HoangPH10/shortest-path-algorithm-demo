# Deployment Guide for Streamlit Cloud

This guide will help you deploy the Route Pathfinding Visualizer to Streamlit Cloud.

## Prerequisites

1. A GitHub account
2. Your code pushed to a GitHub repository
3. A Streamlit Cloud account (free) - sign up at [share.streamlit.io](https://share.streamlit.io)

## Deployment Steps

### 1. Push Your Code to GitHub

Make sure all your code is committed and pushed to GitHub:

```bash
git add .
git commit -m "Add Streamlit Cloud deployment files"
git push
```

### 2. Deploy to Streamlit Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Click "New app" or "Deploy an app"
3. Select your repository from the dropdown
4. Set the following:
   - **Branch**: `main` (or your default branch)
   - **Main file path**: `app.py`
   - **App URL**: Choose a custom URL (optional)

5. Click "Deploy!"

### 3. Wait for Deployment

Streamlit Cloud will:
- Clone your repository
- Install dependencies from `requirements.txt`
- Start your app
- Provide you with a public URL

This usually takes 2-5 minutes.

## Configuration (Optional)

### Environment Variables

If you want to customize the OpenStreetMap user agent or OSRM server:

1. In Streamlit Cloud, go to your app settings
2. Click "Secrets" in the left sidebar
3. Add the following (if needed):

```toml
OSM_USER_AGENT = "YourAppName/1.0"
OSRM_SERVER = "http://router.project-osrm.org"
```

**Note**: The app will work without these as it uses sensible defaults.

### Advanced Settings

In the app settings on Streamlit Cloud, you can also:
- Set Python version (default is usually fine)
- Configure resource allocation
- Set up custom domains

## Files Created for Deployment

- **`requirements.txt`**: Lists all Python dependencies
- **`.streamlit/config.toml`**: Streamlit app configuration (theme, server settings)

## Troubleshooting

### App Won't Start

- Check the logs in Streamlit Cloud for error messages
- Verify all files are pushed to GitHub
- Ensure `requirements.txt` is in the root directory

### Import Errors

- Make sure all dependencies are listed in `requirements.txt`
- Check that the Python version is compatible (3.10+)

### Performance Issues

- The app uses external APIs (Nominatim, OSRM, Overpass)
- API rate limits may apply for free tier
- Consider caching results using `@st.cache_data`

### Map Not Displaying

- Check browser console for errors
- Verify CORS settings in `.streamlit/config.toml`
- Try refreshing the page

## Monitoring Your App

Once deployed, you can:
- View real-time logs
- Monitor resource usage
- See viewer statistics
- Update the app by pushing to GitHub (auto-deploy)

## Cost

Streamlit Cloud offers a free tier with:
- Unlimited public apps
- 1 GB of resources per app
- Community support

For higher resource needs, check [Streamlit Cloud pricing](https://streamlit.io/cloud).

## Additional Resources

- [Streamlit Cloud Documentation](https://docs.streamlit.io/streamlit-community-cloud)
- [Deployment Tutorial](https://docs.streamlit.io/streamlit-community-cloud/get-started/deploy-an-app)
- [Managing Apps](https://docs.streamlit.io/streamlit-community-cloud/manage-your-app)

## Support

If you encounter issues:
- Check [Streamlit Community Forum](https://discuss.streamlit.io/)
- Review [Streamlit Cloud status](https://streamlitstatus.com/)
- Consult the [FAQ](https://docs.streamlit.io/streamlit-community-cloud/get-started/faq)
