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

def scan_registration_files(hackathon_dir):
    """Scan the registration directory for markdown files."""
    registration_dir = os.path.join(hackathon_dir, 'registration')
    if not os.path.exists(registration_dir):
        print(f"Registration directory not found: {registration_dir}")
        return []
        
    files = glob.glob(os.path.join(registration_dir, '*.md'))
    # Exclude template.md
    return [f for f in files if not f.endswith('template.md')]

def scan_demo_files(hackathon_dir):
    """Scan the demos directory for markdown files."""
    demos_dir = os.path.join(hackathon_dir, 'demos')
    if not os.path.exists(demos_dir):
        print(f"Demos directory not found: {demos_dir}")
        return []
        
    files = glob.glob(os.path.join(demos_dir, '*.md'))
    # Exclude template.md
    return [f for f in files if not f.endswith('template.md')]

def generate_hackathon_readme(hackathon_dir, registrations, demos):
    """Generate the README.md for a specific hackathon."""
    readme_path = os.path.join(hackathon_dir, 'README.md')
    
    # Get hackathon name from directory
    hackathon_name = os.path.basename(hackathon_dir).split('-', 1)[1] + " Hackathon"
    
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
        'projects': len(demos),
        'directory': hackathon_dir
    }

def update_main_readme(hackathons_data):
    """Update the main README.md with hackathon information."""
    readme_path = os.path.join(os.getcwd(), 'README.md')
    
    # Try to read existing README to preserve introduction
    introduction = ""
    how_to_participate = ""
    
    try:
        with open(readme_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
            # Extract introduction if it exists
            intro_match = re.search(r'# Casual Hackathon\s+(.+?)(?=##|\Z)', content, re.DOTALL)
            if intro_match:
                introduction = intro_match.group(1).strip()
                
            # Extract how to participate section if it exists
            how_match = re.search(r'## How to Participate\s+(.+?)(?=##|\Z)', content, re.DOTALL)
            if how_match:
                how_to_participate = how_match.group(1).strip()
    except:
        # If README doesn't exist or can't be read, use default content
        introduction = "Welcome to the **Casual Hackathon** platform! This is a place to organize, participate in, and showcase innovative hackathons in the Web3 space. Whether you're a developer, designer, or enthusiast, you can join our hackathons and build amazing projects."
        how_to_participate = """1. Browse the available hackathons in the `hackathons/` directory
2. To register for a hackathon:
   - Navigate to the specific hackathon folder (e.g., `hackathons/1-AI/`)
   - Copy the registration template from the `registration/` folder
   - Create a new file with your username (e.g., `your-username.md`)
   - Fill in all required fields in the template
   - Submit a Pull Request
3. To submit a project:
   - Navigate to the specific hackathon folder
   - Copy the demo template from the `demos/` folder
   - Create a new file with your project name (e.g., `your-project.md`)
   - Fill in all required fields in the template
   - Submit a Pull Request"""
    
    # Generate hackathons table
    hackathons_table = "| Hackathon | Date | Theme | Participants | Projects |\n| --------- | ---- | ----- | ------------ | -------- |\n"
    
    total_participants = 0
    total_projects = 0
    
    for hackathon in hackathons_data:
        # Extract date and theme from README
        hackathon_readme_path = os.path.join(hackathon['directory'], 'README.md')
        date = "TBD"
        theme = "TBD"
        
        try:
            with open(hackathon_readme_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
                # Extract date
                date_match = re.search(r'\*\*Date\*\*:\s*(.+?)(?=\n)', content)
                if date_match:
                    date = date_match.group(1).strip()
                
                # Extract theme
                theme_match = re.search(r'\*\*Theme\*\*:\s*(.+?)(?=\n)', content)
                if theme_match:
                    theme = theme_match.group(1).strip()
        except:
            pass
        
        # Get relative path for the link
        rel_path = os.path.relpath(hackathon_readme_path, os.getcwd())
        
        hackathons_table += f"| [{hackathon['name']}]({rel_path}) | {date} | {theme} | {hackathon['participants']} | {hackathon['projects']} |\n"
        
        total_participants += hackathon['participants']
        total_projects += hackathon['projects']
    
    # Generate README content
    content = [
        "# Casual Hackathon",
        "",
        introduction,
        "",
        "## How to Participate",
        "",
        how_to_participate,
        "",
        "## 🚀 Current Hackathons",
        "",
        hackathons_table,
        "",
        "## 📊 Statistics",
        "",
        f"- **Total Hackathons**: {len(hackathons_data)}",
        f"- **Total Participants**: {total_participants}",
        f"- **Total Projects**: {total_projects}",
        "",
        "---",
        "",
        f"*Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*"
    ]
    
    # Write README
    with open(readme_path, "w", encoding='utf-8') as f:
        f.write("\n".join(content))
    
    print(f"Updated main README.md with {len(hackathons_data)} hackathons")

def update_all_hackathons():
    """Update all hackathon READMEs and the main README."""
    hackathons_dir = os.path.join(os.getcwd(), 'hackathons')
    if not os.path.exists(hackathons_dir):
        print(f"Hackathons directory not found: {hackathons_dir}")
        return
    
    # Get all hackathon directories
    hackathon_dirs = [os.path.join(hackathons_dir, d) for d in os.listdir(hackathons_dir) 
                     if os.path.isdir(os.path.join(hackathons_dir, d))]
    
    hackathons_data = []
    
    for hackathon_dir in hackathon_dirs:
        # Process registration files
        registration_files = scan_registration_files(hackathon_dir)
        registrations = []
        for file in registration_files:
            data = parse_file(file)
            if data and data['type'] == 'registration':
                registrations.append(data)
        
        # Process demo files
        demo_files = scan_demo_files(hackathon_dir)
        demos = []
        for file in demo_files:
            data = parse_file(file)
            if data and data['type'] == 'demo':
                demos.append(data)
        
        # Generate hackathon README
        hackathon_data = generate_hackathon_readme(hackathon_dir, registrations, demos)
        hackathons_data.append(hackathon_data)
    
    # Update main README
    update_main_readme(hackathons_data)

if __name__ == '__main__':
    update_all_hackathons()
