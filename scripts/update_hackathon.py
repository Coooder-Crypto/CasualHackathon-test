import os
import glob
import re
from datetime import datetime

def extract_field(content, field_name):
    """Extract a field value from the content using regex."""
    pattern = rf'{field_name}:\s*"([^"]*)"'
    match = re.search(pattern, content)
    if match:
        return match.group(1)
    return "N/A"

def extract_team_members(content):
    """Extract team members list from the content."""
    pattern = r'team_members:\s*\[(.*?)\]'
    match = re.search(pattern, content)
    if match:
        members_str = match.group(1)
        # Extract quoted strings
        members = re.findall(r'"([^"]*)"', members_str)
        return members
    return []

def parse_file(file_path):
    """Parse a file and extract relevant fields."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
            # Check if this is a registration file
            if "username:" in content:
                return {
                    'type': 'registration',
                    'username': extract_field(content, 'username'),
                    'contact': extract_field(content, 'contact'),
                    'wallet_address': extract_field(content, 'wallet_address'),
                    'role': extract_field(content, 'role'),
                    'team_name': extract_field(content, 'team_name'),
                    'idea': extract_field(content, 'idea'),
                    'support_needed': extract_field(content, 'support_needed'),
                    'notes': extract_field(content, 'notes'),
                    'file_path': file_path
                }
            # Check if this is a demo file
            elif "project_name:" in content:
                return {
                    'type': 'demo',
                    'project_name': extract_field(content, 'project_name'),
                    'description': extract_field(content, 'description'),
                    'project_link': extract_field(content, 'project_link'),
                    'team_members': extract_team_members(content),
                    'presentation_link': extract_field(content, 'presentation_link'),
                    'notes': extract_field(content, 'notes'),
                    'file_path': file_path
                }
            else:
                print(f"Unknown file type: {file_path}")
                return None
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
        return None

def scan_registration_files():
    """Scan the registration directory for markdown files."""
    registration_dir = os.path.join(os.getcwd(), 'registration')
    if not os.path.exists(registration_dir):
        print(f"Registration directory not found: {registration_dir}")
        return []
        
    files = glob.glob(os.path.join(registration_dir, '*.md'))
    # Exclude template.md
    return [f for f in files if not f.endswith('template.md')]

def scan_demo_files():
    """Scan the demos directory for markdown files."""
    demos_dir = os.path.join(os.getcwd(), 'demos')
    if not os.path.exists(demos_dir):
        print(f"Demos directory not found: {demos_dir}")
        return []
        
    files = glob.glob(os.path.join(demos_dir, '*.md'))
    # Exclude template.md
    return [f for f in files if not f.endswith('template.md')]

def generate_hackathon_readme(registrations, demos):
    """Generate the README.md for the hackathon."""
    readme_path = os.path.join(os.getcwd(), 'README.md')
    
    # Get hackathon name from the config or use default
    hackathon_name = "7702 Hackathon"  # Default name, can be customized
    
    # Try to read existing README to preserve custom content
    existing_content = ""
    event_details = ""
    resources = ""
    
    try:
        with open(readme_path, 'r', encoding='utf-8') as f:
            existing_content = f.read()
            
            # Extract event details section if it exists
            event_match = re.search(r'## Event Details\s+(.+?)(?=##|\Z)', existing_content, re.DOTALL)
            if event_match:
                event_details = event_match.group(1).strip()
                
            # Extract resources section if it exists
            resources_match = re.search(r'## Resources\s+(.+?)(?=##|\Z)', existing_content, re.DOTALL)
            if resources_match:
                resources = resources_match.group(1).strip()
    except:
        # If README doesn't exist, use default content
        event_details = "- **Date**: TBD\n- **Location**: TBD\n- **Theme**: TBD"
        resources = "- [Event Schedule](#)\n- [Judging Criteria](#)\n- [Prizes](#)"
    
    # Generate participants table
    participants_table = "| Username | Contact | Role | Team |\n|----------|---------|------|------|\n"
    
    # Statistics
    total_participants = len(registrations)
    teams = set()
    developers = 0
    designers = 0
    
    for reg in registrations:
        username = reg.get('username', 'N/A')
        contact = reg.get('contact', 'N/A')
        role = reg.get('role', 'N/A')
        team_name = reg.get('team_name', 'N/A')
        
        participants_table += f"| {username} | {contact} | {role} | {team_name} |\n"
        
        # Update statistics
        if team_name and team_name != 'N/A':
            teams.add(team_name)
        
        if role and isinstance(role, str):
            role_lower = role.lower()
            if 'developer' in role_lower:
                developers += 1
            elif 'designer' in role_lower:
                designers += 1
    
    # Generate projects table
    projects_table = "| Project Name | Description | Link | Team Members |\n|--------------|-------------|------|-------------|\n"
    
    for demo in demos:
        project_name = demo.get('project_name', 'N/A')
        description = demo.get('description', 'N/A')
        project_link = demo.get('project_link', 'N/A')
        
        # Handle team_members as either a list or a string
        team_members = demo.get('team_members', [])
        if isinstance(team_members, list):
            team_members_str = ", ".join(team_members)
        else:
            team_members_str = str(team_members)
        
        projects_table += f"| {project_name} | {description} | {project_link} | {team_members_str} |\n"
    
    # Generate README content
    content = [
        f"# {hackathon_name}",
        "",
        f"Welcome to the {hackathon_name}!",
        "",
        "## Event Details",
        "",
        event_details,
        "",
        "## Resources",
        "",
        resources,
        "",
        "## Participants",
        "",
        participants_table,
        "",
        "## Projects",
        "",
        projects_table,
        "",
        "## Statistics",
        "",
        f"- **Total Participants**: {total_participants}",
        f"- **Teams**: {len(teams)}",
        f"- **Developers**: {developers}",
        f"- **Designers**: {designers}",
        "",
        f"*Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*"
    ]
    
    # Write README
    with open(readme_path, "w", encoding='utf-8') as f:
        f.write("\n".join(content))
    
    print(f"Updated README.md for {hackathon_name}")
    
    return {
        'name': hackathon_name,
        'participants': total_participants,
        'projects': len(demos)
    }

# This function is no longer needed as we're not aggregating multiple hackathons
# def update_main_readme(hackathons_data):
#     """Update the main README.md with hackathon information."""
#     pass

def update_hackathon():
    """Update the hackathon README with registration and demo information."""
    # Process registration files
    registration_files = scan_registration_files()
    registrations = []
    for file in registration_files:
        data = parse_file(file)
        if data and data['type'] == 'registration':
            registrations.append(data)
    
    # Process demo files
    demo_files = scan_demo_files()
    demos = []
    for file in demo_files:
        data = parse_file(file)
        if data and data['type'] == 'demo':
            demos.append(data)
    
    # Generate hackathon README
    generate_hackathon_readme(registrations, demos)

if __name__ == '__main__':
    update_hackathon()
