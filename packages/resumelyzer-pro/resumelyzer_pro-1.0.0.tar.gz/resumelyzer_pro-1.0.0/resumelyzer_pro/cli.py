import click
import stripe
import webbrowser

@click.group()
def main():
    """Resumelyzer Pro CLI"""
    pass

@main.command()
@click.option('--tier', default='pro', help='Package tier (pro/enterprise)')
def purchase(tier):
    """Start purchase flow"""
    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price': 'price_12345' if tier == 'pro' else 'price_67890',
            'quantity': 1,
        }],
        mode='payment',
        success_url='https://resumelyzer.com/success?session_id={CHECKOUT_SESSION_ID}',
        cancel_url='https://resumelyzer.com/cancel',
    )
    webbrowser.open(session.url)