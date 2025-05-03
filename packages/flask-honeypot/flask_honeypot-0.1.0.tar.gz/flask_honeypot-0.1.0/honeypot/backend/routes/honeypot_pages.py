# honeypot/backend/routes/honeypot_pages.py
from flask import Blueprint, render_template, request, jsonify, make_response, redirect, url_for, current_app
import logging
import time
from datetime import datetime
import json
import hashlib
from werkzeug.local import LocalProxy
from honeypot.database.mongodb import get_db
from honeypot.backend.helpers.db_utils import with_db_recovery


honeypot_pages_bp = Blueprint('honeypot_pages', __name__, 
                              template_folder='templates')


@with_db_recovery
def log_honeypot_interaction(page_type, interaction_type, additional_data=None):
    """Log detailed information about honeypot interactions"""
    try:
        # Get client details
        ip = request.headers.get('X-Forwarded-For', request.remote_addr)
        if ip and ',' in ip:
            ip = ip.split(',')[0].strip()
            
        user_agent = request.headers.get('User-Agent', '')
        referer = request.headers.get('Referer', '')
        
        # Create interaction fingerprint
        interaction_id = hashlib.sha256(f"{ip}|{user_agent}|{time.time()}".encode()).hexdigest()
        
        # Build log entry
        log_entry = {
            "interaction_id": interaction_id,
            "timestamp": datetime.utcnow(),
            "ip_address": ip,
            "user_agent": user_agent,
            "referer": referer,
            "page_type": page_type,
            "interaction_type": interaction_type,
            "http_method": request.method,
            "path": request.path,
            "query_string": dict(request.args),
            "headers": {k: v for k, v in request.headers.items()},
            "cookies": {k: v for k, v in request.cookies.items()},
        }
        
        # Add form data if applicable
        if request.form:
            log_entry["form_data"] = dict(request.form)
            
        # Add JSON data if applicable
        if request.is_json:
            log_entry["json_data"] = request.get_json(silent=True)
            
        # Add additional custom data
        if additional_data:
            log_entry["additional_data"] = additional_data
            
        # Store in database
        db = get_db()
        if db is not None:
            db.honeypot_interactions.insert_one(log_entry)
        else:
            logging.error("Database connection unavailable, interaction not logged")
        
        return interaction_id
    except Exception as e:
        logging.error(f"Error logging honeypot interaction: {str(e)}")
        return None



def determine_category(path):
    """Determine honeypot category based on the request path"""
    path = path.lower()
    
    # WordPress
    if any(x in path for x in ['wp-', 'wordpress', 'wp/', 'wp-login', 'wp-admin']):
        return "wordpress"
    
    # Admin panels
    elif any(x in path for x in ['admin', 'administrator', 'adm', 'siteadmin', 'panel', 'console']):
        return "admin_panels"
    
    # E-commerce
    elif any(x in path for x in ['shop', 'store', 'cart', 'checkout', 'product', 'magento', 'shopify', 'woocommerce']):
        return "e_commerce"
    
    # CMS
    elif any(x in path for x in ['joomla', 'drupal', 'typo3', 'cms', 'content']):
        return "additional_cms"
    
    # Forums and boards
    elif any(x in path for x in ['forum', 'board', 'community', 'discourse', 'phpbb', 'vbulletin']):
        return "forums_and_boards"
    
    # File sharing
    elif any(x in path for x in ['upload', 'file', 'share', 'download', 'ftp', 'webdav']):
        return "file_sharing"
    
    # Database endpoints
    elif any(x in path for x in ['phpmyadmin', 'pma', 'mysql', 'database', 'db', 'sql', 'mongo']):
        return "database_endpoints"
    
    # Mail servers
    elif any(x in path for x in ['mail', 'webmail', 'smtp', 'imap', 'roundcube', 'squirrelmail']):
        return "mail_servers"
    
    # Remote access
    elif any(x in path for x in ['ssh', 'telnet', 'rdp', 'vnc', 'remote']):
        return "remote_access"
    
    # IoT devices
    elif any(x in path for x in ['iot', 'device', 'router', 'camera', 'dvr', 'smart']):
        return "iot_devices"
    
    # DevOps tools
    elif any(x in path for x in ['jenkins', 'gitlab', 'ci', 'cd', 'devops', 'travis', 'build']):
        return "devops_tools"
    
    # Web frameworks
    elif any(x in path for x in ['laravel', 'symfony', 'django', 'flask', 'rails', 'spring']):
        return "web_frameworks"
    
    # Logs and debug
    elif any(x in path for x in ['log', 'debug', 'trace', 'error', 'console']):
        return "logs_and_debug"
    
    # Backdoors and shells
    elif any(x in path for x in ['shell', 'backdoor', 'cmd', 'command', 'c99', 'r57']):
        return "backdoors_and_shells"
    
    # Injection attempts
    elif any(x in path for x in ['sql', 'injection', 'xss', 'script', 'eval']):
        return "injection_attempts"
    
    # Mobile endpoints
    elif any(x in path for x in ['api', 'mobile', 'app', 'android', 'ios', 'endpoint']):
        return "mobile_endpoints"
    
    # Cloud services
    elif any(x in path for x in ['aws', 'azure', 'cloud', 's3', 'bucket', 'lambda']):
        return "cloud_services"
    
    # Monitoring tools
    elif any(x in path for x in ['monitor', 'grafana', 'prometheus', 'nagios', 'zabbix']):
        return "monitoring_tools"
    
    # Special cases for common targets
    if 'phpmyadmin' in path or 'pma' in path:
        return "database_endpoints"
    elif 'cpanel' in path:
        return "admin_panels"
    
    # Return None if no category matched
    return None

@honeypot_pages_bp.route('/system/<path:component>', methods=['GET'])
@with_db_recovery
def system_trap(component):
    """
    Handles the redirection loop with realistic-looking URLs
    """
    # Map URL components to step numbers
    url_mapping = {
        'verify': 1,
        'users/management': 2,
        'access/privileges': 3,
        'security/credentials': 4,
        'vault/passwords': 5,
        'auth/tokens': 6,
        'security/2fa': 7,
        'crypto/keys': 8,
        'data/customers': 9,
        'finance/payments': 10,
        'servers/access': 11,
        'database/dump': 12,
        'developers/api': 13,
        'admin/override': 14,
        'system/root': 15
    }
    
    # Find the current step number from the URL component
    current_step = 1
    for path, step in url_mapping.items():
        if component == path:
            current_step = step
            break
    
    # Determine the next step
    next_step = current_step + 1 if current_step < 15 else 1
    
    # Get the URL component for the next step
    next_component = list(url_mapping.keys())[next_step - 1]
    
    # Log this interaction
    log_honeypot_interaction(
        'system_trap',
        'page_view',
        additional_data={
            'step': current_step,
            'component': component,
            'next_step': next_step,
            'next_component': next_component
        }
    )
    
    # Render the appropriate template
    return render_template(f'redirection/step{current_step}.html', next_component=next_component)


@honeypot_pages_bp.route('/wp-admin', methods=['GET', 'POST'])
@honeypot_pages_bp.route('/wp-login.php', methods=['GET', 'POST'])
@honeypot_pages_bp.route('/wordpress/wp-admin', methods=['GET', 'POST'])
@with_db_recovery
def wordpress_honeypot():
    """WordPress admin honeypot"""
    log_honeypot_interaction('wordpress', 'page_view')
    return render_template('honeypot/wp-dashboard.html')


@honeypot_pages_bp.route('/admin', methods=['GET', 'POST'])
@honeypot_pages_bp.route('/administrator', methods=['GET', 'POST'])
@with_db_recovery
def admin_panel_honeypot():
    """Admin panel honeypot"""
    log_honeypot_interaction('admin_panels', 'page_view')
    return render_template('honeypot/admin-login.html')



# phpMyAdmin routes
@honeypot_pages_bp.route('/phpmyadmin', methods=['GET', 'POST'])
@honeypot_pages_bp.route('/pma', methods=['GET', 'POST'])
@honeypot_pages_bp.route('/mysql', methods=['GET', 'POST'])
@honeypot_pages_bp.route('/db/phpmyadmin', methods=['GET', 'POST'])
@with_db_recovery
def phpmyadmin_honeypot():
    """phpMyAdmin honeypot"""
    log_honeypot_interaction('phpmyadmin', 'page_view')
    return render_template('honeypot/phpmyadmin-dashboard.html')

# cPanel routes
@honeypot_pages_bp.route('/cpanel', methods=['GET', 'POST'])
@honeypot_pages_bp.route('/cPanel', methods=['GET', 'POST'])
@honeypot_pages_bp.route('/cp', methods=['GET', 'POST'])
@with_db_recovery
def cpanel_honeypot():
    """cPanel honeypot"""
    log_honeypot_interaction('cpanel', 'page_view')
    return render_template('honeypot/cpanel-dashboard.html')

# Admin panel routes
@honeypot_pages_bp.route('/admin/login', methods=['GET', 'POST'])
@honeypot_pages_bp.route('/admin/dashboard', methods=['GET', 'POST'])
@honeypot_pages_bp.route('/adminpanel', methods=['GET', 'POST'])
@with_db_recovery
def admin_honeypot():
    """Generic admin honeypot"""
    log_honeypot_interaction('admin_panels', 'page_view')
    return render_template('honeypot/admin-dashboard.html')

# E-commerce admin routes
@honeypot_pages_bp.route('/shop/admin', methods=['GET', 'POST'])
@honeypot_pages_bp.route('/store/admin', methods=['GET', 'POST'])
@honeypot_pages_bp.route('/woocommerce/admin', methods=['GET', 'POST'])
@honeypot_pages_bp.route('/magento/admin', methods=['GET', 'POST'])
@honeypot_pages_bp.route('/shopify/admin', methods=['GET', 'POST'])
@with_db_recovery
def ecommerce_honeypot():
    """E-commerce admin honeypot"""
    log_honeypot_interaction('ecommerce', 'page_view')
    return render_template('honeypot/ecommerce-dashboard.html')

# Additional CMS routes
@honeypot_pages_bp.route('/typo3', methods=['GET', 'POST'])
@honeypot_pages_bp.route('/joomla/administrator', methods=['GET', 'POST'])
@honeypot_pages_bp.route('/drupal/admin', methods=['GET', 'POST'])
@honeypot_pages_bp.route('/craft/admin', methods=['GET', 'POST'])
@honeypot_pages_bp.route('/cms/admin', methods=['GET', 'POST'])
@with_db_recovery
def cms_honeypot():
    """CMS admin honeypot"""
    log_honeypot_interaction('additional_cms', 'page_view')
    return render_template('honeypot/cms-dashboard.html')

# Forums and boards routes
@honeypot_pages_bp.route('/forum/admin', methods=['GET', 'POST'])
@honeypot_pages_bp.route('/phpbb/admin', methods=['GET', 'POST'])
@honeypot_pages_bp.route('/vbulletin/admincp', methods=['GET', 'POST'])
@honeypot_pages_bp.route('/xenforo/admin', methods=['GET', 'POST'])
@honeypot_pages_bp.route('/community/admin', methods=['GET', 'POST'])
@with_db_recovery
def forum_honeypot():
    """Forum admin honeypot"""
    log_honeypot_interaction('forums_and_boards', 'page_view')
    return render_template('honeypot/forum-dashboard.html')

# File sharing routes
@honeypot_pages_bp.route('/owncloud/login', methods=['GET', 'POST'])
@honeypot_pages_bp.route('/nextcloud/login', methods=['GET', 'POST'])
@honeypot_pages_bp.route('/cloud/admin', methods=['GET', 'POST'])
@honeypot_pages_bp.route('/filerun/admin', methods=['GET', 'POST'])
@honeypot_pages_bp.route('/share/admin', methods=['GET', 'POST'])
@with_db_recovery
def file_sharing_honeypot():
    """File sharing admin honeypot"""
    log_honeypot_interaction('file_sharing', 'page_view')
    return render_template('honeypot/filesharing-dashboard.html')

# Database endpoints routes
@honeypot_pages_bp.route('/mongodb', methods=['GET', 'POST'])
@honeypot_pages_bp.route('/postgres', methods=['GET', 'POST'])
@honeypot_pages_bp.route('/redis', methods=['GET', 'POST'])
@honeypot_pages_bp.route('/elasticsearch', methods=['GET', 'POST'])
@honeypot_pages_bp.route('/couchdb/_utils', methods=['GET', 'POST'])
@with_db_recovery
def database_honeypot():
    """Database admin honeypot"""
    log_honeypot_interaction('database_endpoints', 'page_view')
    return render_template('honeypot/database-dashboard.html')

# Mail server routes
@honeypot_pages_bp.route('/webmail', methods=['GET', 'POST'])
@honeypot_pages_bp.route('/roundcube', methods=['GET', 'POST'])
@honeypot_pages_bp.route('/squirrelmail', methods=['GET', 'POST'])
@honeypot_pages_bp.route('/mail/admin', methods=['GET', 'POST'])
@honeypot_pages_bp.route('/postfixadmin', methods=['GET', 'POST'])
@with_db_recovery
def mail_server_honeypot():
    """Mail server admin honeypot"""
    log_honeypot_interaction('mail_servers', 'page_view')
    return render_template('honeypot/mail-dashboard.html')

# Remote access routes
@honeypot_pages_bp.route('/ssh', methods=['GET', 'POST'])
@honeypot_pages_bp.route('/vnc', methods=['GET', 'POST'])
@honeypot_pages_bp.route('/rdp', methods=['GET', 'POST'])
@honeypot_pages_bp.route('/webssh', methods=['GET', 'POST'])
@honeypot_pages_bp.route('/terminal', methods=['GET', 'POST'])
@with_db_recovery
def remote_access_honeypot():
    """Remote access honeypot"""
    log_honeypot_interaction('remote_access', 'page_view')
    return render_template('honeypot/remote-access-dashboard.html')

# IoT devices routes
@honeypot_pages_bp.route('/router', methods=['GET', 'POST'])
@honeypot_pages_bp.route('/camera', methods=['GET', 'POST'])
@honeypot_pages_bp.route('/ipcam', methods=['GET', 'POST'])
@honeypot_pages_bp.route('/smart-home', methods=['GET', 'POST'])
@honeypot_pages_bp.route('/device/admin', methods=['GET', 'POST'])
@with_db_recovery
def iot_device_honeypot():
    """IoT device admin honeypot"""
    log_honeypot_interaction('iot_devices', 'page_view')
    return render_template('honeypot/iot-dashboard.html')

# DevOps tools routes
@honeypot_pages_bp.route('/jenkins', methods=['GET', 'POST'])
@honeypot_pages_bp.route('/gitlab', methods=['GET', 'POST'])
@honeypot_pages_bp.route('/travis', methods=['GET', 'POST'])
@honeypot_pages_bp.route('/circleci', methods=['GET', 'POST'])
@honeypot_pages_bp.route('/kubernetes', methods=['GET', 'POST'])
@with_db_recovery
def devops_honeypot():
    """DevOps tools honeypot"""
    log_honeypot_interaction('devops_tools', 'page_view')
    return render_template('honeypot/devops-dashboard.html')

# Web frameworks routes
@honeypot_pages_bp.route('/django/admin', methods=['GET', 'POST'])
@honeypot_pages_bp.route('/rails/admin', methods=['GET', 'POST'])
@honeypot_pages_bp.route('/laravel/admin', methods=['GET', 'POST'])
@honeypot_pages_bp.route('/spring/admin', methods=['GET', 'POST'])
@honeypot_pages_bp.route('/flask/admin', methods=['GET', 'POST'])
@with_db_recovery
def framework_honeypot():
    """Web framework admin honeypot"""
    log_honeypot_interaction('web_frameworks', 'page_view')
    return render_template('honeypot/framework-dashboard.html')

# Logs and debug routes
@honeypot_pages_bp.route('/logs', methods=['GET', 'POST'])
@honeypot_pages_bp.route('/debug', methods=['GET', 'POST'])
@honeypot_pages_bp.route('/debug/console', methods=['GET', 'POST'])
@honeypot_pages_bp.route('/debug/panel', methods=['GET', 'POST'])
@honeypot_pages_bp.route('/trace', methods=['GET', 'POST'])
@with_db_recovery
def debug_honeypot():
    """Logs and debug honeypot"""
    log_honeypot_interaction('logs_and_debug', 'page_view')
    return render_template('honeypot/debug-console.html')

# Backdoors and shells routes
@honeypot_pages_bp.route('/shell.php', methods=['GET', 'POST'])
@honeypot_pages_bp.route('/c99.php', methods=['GET', 'POST'])
@honeypot_pages_bp.route('/cmd.php', methods=['GET', 'POST'])
@honeypot_pages_bp.route('/backdoor.php', methods=['GET', 'POST'])
@honeypot_pages_bp.route('/terminal.php', methods=['GET', 'POST'])
@with_db_recovery
def shell_honeypot():
    """Backdoor/shell honeypot"""
    log_honeypot_interaction('backdoors_and_shells', 'page_view')
    return render_template('honeypot/shell.html')

# Injection attempts routes
@honeypot_pages_bp.route('/page.php', methods=['GET', 'POST'])
@honeypot_pages_bp.route('/article.php', methods=['GET', 'POST'])
@honeypot_pages_bp.route('/product.php', methods=['GET', 'POST'])
@honeypot_pages_bp.route('/user.php', methods=['GET', 'POST'])
@honeypot_pages_bp.route('/view.php', methods=['GET', 'POST'])
@with_db_recovery
def injection_honeypot():
    """Injection vulnerabilities honeypot"""
    # Log any parameters passed
    params = {k: v for k, v in request.args.items()}
    log_honeypot_interaction('injection_attempts', 'page_view', additional_data={'params': params})
    return render_template('honeypot/generic-page.html')

# Mobile endpoints routes
@honeypot_pages_bp.route('/api/mobile', methods=['GET', 'POST'])
@honeypot_pages_bp.route('/api/v1/mobile', methods=['GET', 'POST'])
@honeypot_pages_bp.route('/mobile/api', methods=['GET', 'POST'])
@honeypot_pages_bp.route('/app/api', methods=['GET', 'POST'])
@honeypot_pages_bp.route('/api/app', methods=['GET', 'POST'])
@with_db_recovery
def mobile_api_honeypot():
    """Mobile API honeypot"""
    # Log any JSON data
    json_data = request.get_json(silent=True) or {}
    log_honeypot_interaction('mobile_endpoints', 'page_view', additional_data={'json_data': json_data})
    return render_template('honeypot/mobile-api.html')

# Cloud services routes
@honeypot_pages_bp.route('/aws/login', methods=['GET', 'POST'])
@honeypot_pages_bp.route('/azure/login', methods=['GET', 'POST'])
@honeypot_pages_bp.route('/gcp/login', methods=['GET', 'POST'])
@honeypot_pages_bp.route('/s3/console', methods=['GET', 'POST'])
@honeypot_pages_bp.route('/ec2/console', methods=['GET', 'POST'])
@with_db_recovery
def cloud_honeypot():
    """Cloud services honeypot"""
    log_honeypot_interaction('cloud_services', 'page_view')
    return render_template('honeypot/cloud-dashboard.html')

# Monitoring tools routes
@honeypot_pages_bp.route('/nagios', methods=['GET', 'POST'])
@honeypot_pages_bp.route('/zabbix', methods=['GET', 'POST'])
@honeypot_pages_bp.route('/grafana', methods=['GET', 'POST'])
@honeypot_pages_bp.route('/prometheus', methods=['GET', 'POST'])
@honeypot_pages_bp.route('/monitoring', methods=['GET', 'POST'])
@with_db_recovery
def monitoring_honeypot():
    """Monitoring tools honeypot"""
    log_honeypot_interaction('monitoring_tools', 'page_view')
    return render_template('honeypot/monitoring-dashboard.html')

@honeypot_pages_bp.route('/<path:path>', methods=['GET', 'POST'])
@with_db_recovery
def catch_all_honeypot(path):
    """Catch-all route that categorizes and redirects to specific honeypot handlers"""
    # Determine category from path
    category = determine_category(path)
    
    if category == "wordpress":
        return redirect(url_for('honeypot_pages.wordpress_honeypot'))
    elif category == "admin_panels":
        return redirect(url_for('honeypot_pages.admin_honeypot')) 
    elif category == "e_commerce":
        return redirect(url_for('honeypot_pages.ecommerce_honeypot'))
    elif category == "additional_cms":
        return redirect(url_for('honeypot_pages.cms_honeypot'))
    elif category == "forums_and_boards":
        return redirect(url_for('honeypot_pages.forum_honeypot'))
    elif category == "file_sharing":
        return redirect(url_for('honeypot_pages.file_sharing_honeypot'))  
    elif category == "mail_servers":
        return redirect(url_for('honeypot_pages.mail_server_honeypot'))  
    elif category == "remote_access":
        return redirect(url_for('honeypot_pages.remote_access_honeypot'))
    elif category == "iot_devices":
        return redirect(url_for('honeypot_pages.iot_device_honeypot'))  
    elif category == "devops_tools":
        return redirect(url_for('honeypot_pages.devops_honeypot'))
    elif category == "web_frameworks":
        return redirect(url_for('honeypot_pages.framework_honeypot'))
    elif category == "logs_and_debug":
        return redirect(url_for('honeypot_pages.debug_honeypot'))
    elif category == "backdoors_and_shells":
        return redirect(url_for('honeypot_pages.shell_honeypot'))
    elif category == "injection_attempts":
        return redirect(url_for('honeypot_pages.injection_honeypot'))
    elif category == "mobile_endpoints":
        return redirect(url_for('honeypot_pages.mobile_api_honeypot'))  
    elif category == "cloud_services":
        return redirect(url_for('honeypot_pages.cloud_honeypot'))
    elif category == "monitoring_tools":
        return redirect(url_for('honeypot_pages.monitoring_honeypot'))
    
    if 'phpmyadmin' in path or 'pma' in path:
        return redirect(url_for('honeypot_pages.phpmyadmin_honeypot'))
    elif 'cpanel' in path:
        return redirect(url_for('honeypot_pages.cpanel_honeypot'))
    elif 'admin' in path:
        return redirect(url_for('honeypot_pages.admin_honeypot'))
    
    return render_template('honeypot/generic-login.html')
