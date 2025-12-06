from subprocess import run, PIPE

def test_cli_greet():
    p = run(['python', 'generated/cli_greet.py', 'Ariyan'], stdout=PIPE, text=True)
    assert "Hello, Ariyan!" in p.stdout
