import click
import requests

from cli.utils.config import get_config, save_config
from cli.utils.token import save_token


@click.command()
@click.option("--server", "-s", help="서버 URL")
@click.option("--api-key", "-k", help="API 키로 로그인 (CI/CD 환경용)")
def login(server, api_key):
    """서버에 로그인

    API 키를 입력받아 저장합니다.
    저장된 API 키는 이후 모든 요청의 x-api-key 헤더에 포함됩니다.
    """
    try:
        # 설정 파일 읽기
        config = get_config()

        if server:
            config["server"] = server

        server_url = config.get("server")

        if not server_url:
            click.echo(
                "서버 URL이 설정되지 않았습니다. 명령어 예시: deeply-vault login -s http://localhost:13500")
            return

        # API 키 입력 또는 확인
        if not api_key:
            api_key = click.prompt("API 키를 입력하세요", hide_input=True)

        # API 키 유효성 검증
        response = requests.get(
            f"{server_url}/api/v1/auth/me",
            headers={
                "x-api-key": api_key,
                "Content-Type": "application/json"
            }
        )

        if response.status_code != 200:
            click.echo(
                f"API 키 검증 실패: {response.json().get('detail', '알 수 없는 오류')}", err=True)
            return

        # API 키 저장
        save_token(api_key)

        # 설정 파일 업데이트
        save_config(config)

        click.echo("API 키가 ~/.deeply/vault/token.json에 저장되었습니다.")

    except Exception as e:
        click.echo(f"오류가 발생했습니다: {str(e)}", err=True)
