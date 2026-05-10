import json, csv
from datetime import datetime

class Finding:
    def __init__(self, title, severity, evidence='', details='', timestamp=None):
        self.title = title
        self.severity = severity.capitalize()
        self.evidence = evidence
        self.details = details
        self.timestamp = timestamp if timestamp else datetime.utcnow().isoformat() + 'Z'

    def to_dict(self):
        return {
            'title': self.title,
            'severity': self.severity,
            'evidence': self.evidence,
            'details': self.details,
            'timestamp': self.timestamp
        }

class ReportEngine:
    def __init__(self):
        self.findings = []

    def add(self, title, severity, evidence='', details=''):
        self.findings.append(Finding(title, severity, evidence, details))

    def export_json(self, filepath):
        with open(filepath, 'w') as f:
            json.dump([f_.to_dict() for f_ in self.findings], f, indent=2)
        print(f"[Report] JSON exported to {filepath}")

    def export_csv(self, filepath):
        with open(filepath, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['title','severity','evidence','details','timestamp'])
            writer.writeheader()
            for f_ in self.findings:
                writer.writerow(f_.to_dict())
        print(f"[Report] CSV exported to {filepath}")

    def export_html(self, filepath):
        html = ['<html><head><title>Pentest Report</title></head><body><h1>Findings</h1><table border="1"><tr><th>Title</th><th>Severity</th><th>Evidence</th><th>Timestamp</th></tr>']
        for f_ in self.findings:
            evidence = str(f_.evidence).replace('<','&lt;').replace('>','&gt;')
            html.append(f'<tr><td>{f_.title}</td><td>{f_.severity}</td><td>{evidence}</td><td>{f_.timestamp}</td></tr>')
        html.append('</table></body></html>')
        with open(filepath, 'w') as f:
            f.write('\n'.join(html))
        print(f"[Report] HTML exported to {filepath}")

    def export_markdown(self, filepath):
        md = ['# Pentest Findings', '', '| Title | Severity | Evidence | Timestamp |',
              '|-------|----------|----------|-----------|']
        for f_ in self.findings:
            evidence = str(f_.evidence).replace('|','\\|').replace('\n',' ')
            md.append(f'| {f_.title} | {f_.severity} | {evidence} | {f_.timestamp} |')
        with open(filepath, 'w') as f:
            f.write('\n'.join(md))
        print(f"[Report] Markdown exported to {filepath}")