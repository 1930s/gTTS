from gtts import gTTS, Languages, __version__
import sys, os, codecs, click

# Click settings
CONTEXT_SETTINGS = {
    'help_option_names': ['-h', '--help']
}

def validate_text(ctx, param, value):
    """Validation callback for the 'text' argument. 
    Ensures 'text' (arg) and 'file' (opt) are mutually exclusive
    """
    if not value and 'file' not in ctx.params:
        # No <text> and no <file>
        raise click.BadParameter("TEXT or -f/--file PATH required")
    if value and 'file' in ctx.params:
        # Both <text> and <file>
        raise click.BadParameter("TEXT and -f/--file PATH can't be used together")
    return value

def print_languages(ctx, param, value):
    """Prints sorted pretty-printed list of supported languages"""
    if not value or ctx.resilient_parsing:
        return
    langs = Languages().get()
    click.echo('  '+'\n  '.join(sorted("{}: {}".format(k, langs[k]) for k in langs)))
    ctx.exit()

@click.command(context_settings=CONTEXT_SETTINGS)
@click.argument('text', required=False, callback=validate_text)
@click.option('-f', '--file',
    type=click.File(),
    help="Input is contents of PATH instead of TEXT (use '-' for stdin).")
@click.option('-o', '--output',
    type=click.File(mode='wb'),
    help="Write to PATH instead of stdout.")
@click.option('-s', '--slow', default=False, is_flag=True,
    help="Read more slowly.")
@click.option('-l', '--lang', default='en',
    help="IETF language tag. Language to speak in. List documented tags with -a/--all.")
@click.option('-x', '--nocheck', default=False, is_flag=True,
    help="Disable strick IETF language tag checking. Allows undocumented tags.")
@click.option('-a', '--all', default=False, is_flag=True, callback=print_languages,
    expose_value=False, is_eager=True,
    help="Print all documented available IETF language tags and exit.")
@click.option('--debug', default=False, is_flag=True, help="Show debug information.")
@click.version_option(version=__version__)
def tts_cli(text, file, output, slow, lang, nocheck, debug):
    """Reads TEXT to MP3 format using Google Translate's Text-to-Speech API.

    (use '-' as TEXT or as -f/--file PATH for stdin)
    """
    
    # Language check
    # (We can't do callback validation on <lang> because we
    # have to check against <nocheck> which might not exist
    # in the Click context at the time <lang> is used)
    if not nocheck:
        langs_list = Languages().get_list()
        if lang not in langs_list:
            msg = "Use --all to list languages, or add ---nocheck to disable language check."
            raise click.BadParameter(msg, param_hint="lang")

    # stdin for <text> (auto for <file>)
    if text is '-':
        text = click.get_text_stream('stdin').read()
    
    # stdout (when no <output>)
    if not output:
        output = click.get_binary_stream('stdout')

    # <file> input
    if file: text = file.read() 

    # TTS
    tts = gTTS(text=text, lang=lang, slow=slow, lang_check=nocheck, debug=debug)
    tts.write_to_fp(output)
