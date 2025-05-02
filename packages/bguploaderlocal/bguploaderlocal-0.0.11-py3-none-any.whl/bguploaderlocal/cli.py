import argparse
import os
from .uploader import upload_file, upload_xml_files_from_folder
from .config import Config
from rich import print

def run():
	parser = argparse.ArgumentParser(description="Upload a single .xml file or all .xml files in a folder to an API endpoint.")
	parser.add_argument('action', choices=['UPLOAD_RESULTS'], help='Action to do')
	parser.add_argument('path', help='Path to .xml file or folder containing .xml files')
	parser.add_argument('--api_key', required=True, help='Bugasura API Key')
	parser.add_argument('--team_id', required=True, help='Bugasura Team Id')
	parser.add_argument('--project_id', required=True, help='Bugasura Project Id')
	parser.add_argument('--testrun_id', required=False, help='Bugasura Testrun Id. If not passed, new Testrun will be created in the Bugasura Project')
	parser.add_argument('--server', required=False, choices=['local', 'live', 'stage', 'facilio', 'shoppersstop', 'frammer', 'jupiter', 'trustrace', 'testpert'], help='Enterprise Server Names')
	args = parser.parse_args()
	api_base_url = "http://localhost/api.appachhi.com/"

	if args.server:
		if args.server.lower() == "local":
			api_base_url = "http://localhost/api.appachhi.com/"
		elif args.server.lower() == "stage":
			api_base_url = "https://api.stage.bugasura.io/"
		elif args.server.lower() == "live":
			api_base_url = "https://api.bugasura.io/"
		elif args.server.lower() == "facilio":
			api_base_url = "https://api.facilio.bugasura.io/"
		elif args.server.lower() == "shoppersstop":
			api_base_url = "https://api.shoppersstop.bugasura.io/"
		elif args.server.lower() == "frammer":
			api_base_url = "https://api.frammer.bugasura.io/"
		elif args.server.lower() == "jupiter":
			api_base_url = "https://api.jupiter.bugasura.io/"
		elif args.server.lower() == "trustrace":
			api_base_url = "https://api.trustrace.bugasura.io/"
		elif args.server.lower() == "testpert":
			api_base_url = "https://api.testpert.bugasura.io/"

	if not args.testrun_id:
		args.testrun_id = ''

	if not args.action:
		args.action = 'UPLOAD_RESULTS'

	try:
		if os.path.isfile(args.path):
			result = upload_file(args.path, args.api_key, args.team_id, args.project_id, args.testrun_id, api_base_url)
			report_link = result.get('apiResponse', {}).get('reportLink')
			if report_link:
				print(f"[bold green]Upload successful![/bold green] [bold magenta]🔗 Bugasura Test Run Link: [/bold magenta] [link={report_link}]{report_link}[/link]")
			else:
				print("[bold green]Upload successful![/bold green]")
		elif os.path.isdir(args.path):
			result = upload_xml_files_from_folder(args.path, args.api_key, args.team_id, args.project_id, args.testrun_id, api_base_url)
			report_link = result.get('apiResponse', {}).get('reportLink')
			if report_link:
				print(f"[bold green]Upload successful![/bold green] [bold magenta]🔗 Bugasura Test Run Link: [/bold magenta] [link={report_link}]{report_link}[/link]")
			else:
				print("[bold green]Upload successful![/bold green]")
		else:
			raise ValueError(f"[bold red]Invalid path: {args.path}[/bold red]")
	except Exception as e:
		print(f"[bold red]❌ Upload failed: {str(e)}[/bold red]")