import os, json, boto3
import google.generativeai as genai
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-2.5-flash')
ec2 = boto3.resource('ec2', region_name='us-east-1')

def get_ai_decision(user_input):
    """Asks AI if the user wants a server and what to name it."""
    prompt = f"""
    Analyze: "{user_input}" Return JSON ONLY: {{ "create_server": true/false, "server_name": "suggested_name", "reply": "short response to user"}}
    """
    response = model.generate_content(prompt).text
    # Simple cleanup to ensure valid JSON
    return json.loads(response.replace('```json', '').replace('```', '').strip())

def launch_server(name):
    """Creates a basic EC2 instance."""
    try:
        try: 
            ec2.meta.client.create_key_pair(KeyName=f"{name}_key")
        except: 
            pass
        try:
            sg = ec2.create_security_group(GroupName=f"{name}_sg", Description="AI Created")
            sg.authorize_ingress(IpProtocol='tcp', FromPort=22, ToPort=22, CidrIp='0.0.0.0/0')
            sg_id = sg.id
        except Exception as e:
            sgs = list(ec2.security_groups.filter(Filters=[{'Name': 'group-name', 'Values': [f"{name}_sg"]}]))
            if sgs:
                sg_id = sgs[0].id
            else:
                raise e
        instance = ec2.create_instances(
            ImageId='ami-04b4f1a9cf54c11d0', MinCount=1, MaxCount=1, InstanceType='t3.micro', KeyName=f"{name}_key", SecurityGroupIds=[sg_id],
            TagSpecifications=[{'ResourceType': 'instance', 'Tags': [{'Key': 'Name', 'Value': name}]}]
        )[0]
        
        return {"success": True, "id": instance.id}
        
    except Exception as e:
        return {"success": False, "error": str(e)}
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    user_text = request.json.get('message', '')
    decision = get_ai_decision(user_text)

    if decision.get('create_server'):
        result = launch_server(decision['server_name'])
        if result['success']:
            return jsonify({
                "response": f"{decision['reply']} (Created Instance ID: {result['id']})",
                "success": True
            })
        else:
            return jsonify({
                "response": f"I tried to create the server but AWS returned an error: {result['error']}",
                "success": False
            })
    return jsonify({"response": decision['reply'], "success": True})

if __name__ == '__main__':
    app.run(debug=True, port=5000)