from flask import Flask, render_template, request, jsonify, send_file
from research_agent import ResearchAgent
from presentation_generator import PresentationGenerator
import os
import threading
from datetime import datetime
import markdown
import secrets

app = Flask(__name__)

# Secure configuration
app.config.update(
    SECRET_KEY=os.getenv('SECRET_KEY', secrets.token_hex(32)),
    DEBUG=os.getenv('FLASK_ENV') != 'production',
    MAX_CONTENT_LENGTH=16 * 1024 * 1024
)

# Store research results (in production, use Redis or database)
research_results = {}

class ResearchThread(threading.Thread):
    def __init__(self, topic, result_id):
        threading.Thread.__init__(self)
        self.topic = topic
        self.result_id = result_id
        self.daemon = True
    
    def run(self):
        try:
            research_agent = ResearchAgent()
            presentation_gen = PresentationGenerator()
            
            # Update progress
            research_results[self.result_id]['status'] = 'searching'
            research_results[self.result_id]['message'] = '🔍 Searching for reliable sources...'
            
            # Conduct research
            research_data = research_agent.research_topic(self.topic)
            
            # Update progress
            research_results[self.result_id]['status'] = 'analyzing'
            research_results[self.result_id]['message'] = '🤖 Analyzing content with AI...'
            
            # Generate presentation
            presentation = presentation_gen.generate_presentation(research_data, self.topic)
            
            # Save to file
            filename = f"research_presentation_{self.result_id}.md"
            filepath = os.path.join('uploads', filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(presentation)
            
            # Convert to HTML for display
            html_content = markdown.markdown(presentation)
            
            research_results[self.result_id] = {
                'status': 'completed',
                'topic': self.topic,
                'presentation': presentation,
                'html_content': html_content,
                'filename': filename,
                'filepath': filepath,
                'timestamp': datetime.now().isoformat(),
                'message': '✅ Research completed!'
            }
            
        except Exception as e:
            research_results[self.result_id] = {
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.now().isoformat(),
                'message': '❌ Research failed'
            }

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/research', methods=['POST'])
def start_research():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No JSON data provided'}), 400
    
    topic = data.get('topic', '').strip()
    if not topic:
        return jsonify({'error': 'Topic is required'}), 400
    
    if len(topic) > 200:
        return jsonify({'error': 'Topic too long (max 200 characters)'}), 400
    
    # Generate unique ID for this research
    result_id = datetime.now().strftime("%Y%m%d%H%M%S%f")
    
    # Initialize research entry
    research_results[result_id] = {
        'status': 'initializing',
        'topic': topic,
        'timestamp': datetime.now().isoformat(),
        'message': '🚀 Initializing research...'
    }
    
    # Start research in background thread
    research_thread = ResearchThread(topic, result_id)
    research_thread.start()
    
    return jsonify({
        'result_id': result_id,
        'status': 'initializing',
        'message': 'Research started successfully!'
    })

@app.route('/research/<result_id>')
def get_research_status(result_id):
    if not result_id.isalnum() or len(result_id) > 50:
        return jsonify({'error': 'Invalid research ID'}), 400
    
    result = research_results.get(result_id, {})
    if not result:
        return jsonify({'error': 'Research not found'}), 404
    
    return jsonify(result)

@app.route('/download/<result_id>')
def download_presentation(result_id):
    if not result_id.isalnum() or len(result_id) > 50:
        return jsonify({'error': 'Invalid research ID'}), 400
    
    result = research_results.get(result_id, {})
    if result.get('status') != 'completed':
        return jsonify({'error': 'Research not completed'}), 400
    
    filepath = result.get('filepath')
    if not filepath or not os.path.exists(filepath):
        return jsonify({'error': 'File not found'}), 404
    
    safe_topic = "".join(c for c in result['topic'] if c.isalnum() or c in (' ', '-', '_')).rstrip()
    download_name = f"research_{safe_topic}.md"
    
    return send_file(filepath, as_attachment=True, download_name=download_name)

@app.route('/health')
def health_check():
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Resource not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    # Create uploads directory if it doesn't exist
    os.makedirs('uploads', exist_ok=True)
    
    # Get host and port from environment
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', 5000))
    
    print(f"🚀 Starting AI Research Agent on {host}:{port}")
    print("📝 Environment:", os.getenv('FLASK_ENV', 'development'))
    
    app.run(host=host, port=port, debug=os.getenv('FLASK_ENV') != 'production')