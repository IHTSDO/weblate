# Translation Tool Deployment and Setup

Follow these steps to deploy the translation tool and complete setup via the management dashboard.

## Weblate Deployment
The steps and commands for deployment are listed in `install-steps.txt`. 

Once complete Weblate should be deployed and running under the Gunicorn service, hosted by Nginx.  
Confirm that it's running using:
```
sudo systemctl status gunicorn
```
Use the steps below to complete the setup.  

## Admin Users Setup
1. Login to Simplex to get authenticated
2. Access weblate (uses single-sign-on), to create the internal user record.
3. Create weblate **admin** user:
```
cd /opt/weblate/weblate-env/
sudo su weblate
. bin/activate
weblate createadmin
```
Make a note of the generated password.

4. Disable Weblate SSO authentication
   - Edit /etc/nginx/conf.d/weblate.conf, comment out line "auth_request /auth" within "location /"
   - Reload nginx `sudo nginx -s reload`
5. Login to Weblate as **admin** via URL /accounts/login/
6. Grant admin users "super-admin" role
   - Find user under /manage/users/, select and click Edit
   - Check box "Superuser status"
   - Save
7. Enable Weblate SSO authentication
    - Uncomment nginx "auth_request /auth" line within "location /"
    - Reload nginx `sudo nginx -s reload`
8. Log out of Simplex and ensure access is denied to Weblate

## Complete Git Repository Setup
Login to Simplex with an account that has Weblate super-user status.
Access the Weblate management page at URL /manage/. In the **SSH keys** page take the "Public RSA SSH key" and add that to the github repo with write access, using deploy keys section or other method.

## Appearance Setup
As an admin user navigate to the management appearance screen under /manage/appearance/.

Change the following RGB colours:
- Navigation color (Light) = 18 / 79 / 107
- Focus color (Light) = 0 / 169 / 224
- Hover color (Light) = 100 / 190 / 224

Also select "Hide page footer".
