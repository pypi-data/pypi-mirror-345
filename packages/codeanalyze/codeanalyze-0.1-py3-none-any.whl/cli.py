import click
import requests

API_URL = "https://ai-powered-code-security-analyzer.onrender.com"

@click.group()
def cli():
    """AI 기반 보안 분석기 CLI"""
    pass

@cli.command()
@click.option("--file", "-f", type=click.Path(exists=True), help="분석할 코드 파일")
def analyze(file):
    with open(file, "r") as f:
        code = f.read()

    payload = {"code": code}
    try:
        res = requests.post(f"{API_URL}/analyze", json=payload, timeout=120)
        res.raise_for_status()
        result = res.json()

        click.echo(f"🛡️ 예측 결과: {result['prediction']}")
        click.echo(f"🔖 라벨: {result['label']}")
        click.echo(f"📊 보안 점수: {result['security_score']}")
    except Exception as e:
        click.echo(f"❌ 에러 발생: {e}")

@cli.command()
@click.option("--file", "-f", type=click.Path(exists=True), help="리포트 생성할 코드 파일")
@click.option("--docx", is_flag=True, help="DOCX 리포트 다운로드")
def report(file, docx):
    with open(file, "r") as f:
        code = f.read()

    payload = {"code": code}
    try:
        res = requests.post(f"{API_URL}/report/docx", json=payload, timeout=180)
        res.raise_for_status()
        with open("Security_Report.docx", "wb") as f:
            f.write(res.content)
        click.echo("📄 Security_Report.docx 파일이 생성되었습니다.")
    except Exception as e:
        click.echo(f"❌ 에러 발생: {e}")