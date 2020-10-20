from flask import Flask, render_template, url_for, request, abort

import stripe

app = Flask(__name__)

app.config['STRIPE_PUBLIC_KEY'] = 'pk_test_51HdxovB6KrRuwHV6JVCl9dlIU2E4mXA1sdLM6roIZM7o7yaLe5LGniJSyI6qB51eXMq31yz9zPt7SxNHL3Znq5Ak00UBH32TB2'
app.config['STRIPE_SECRET_KEY'] = 'sk_test_51HdxovB6KrRuwHV6gjYobKMwj7PJV5OMzWELD5Y7gXW0vSYfoJ75iZPRIVNTYcTAUV62xBTKrMesMmSnMjrjGtm500y1Djh0MK'

stripe.api_key = app.config['STRIPE_SECRET_KEY']

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/stripe_pay')
def stripe_pay():
    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price': 'price_1HeINeB6KrRuwHV6kb66NZM3',
            'quantity': 1,
        }],
        mode='payment',
        success_url=url_for('thanks', _external=True) + '?session_id={CHECKOUT_SESSION_ID}',
        cancel_url=url_for('index', _external=True),
    )
    return {
        'checkout_session_id': session['id'],
        'checkout_public_key': app.config['STRIPE_PUBLIC_KEY']
    }

@app.route('/thanks')
def thanks():
    return render_template('thanks.html')

@app.route('/stripe_webhook', methods=['POST'])
def stripe_webhook():
    print('WEBHOOK CALLED')

    if request.content_length > 1024 * 1024:
        print('REQUEST TOO BIG')
        abort(400)
    payload = request.get_data()
    sig_header = request.environ.get('HTTP_STRIPE_SIGNATURE')
    endpoint_secret = 'whsec_Bq0oOBZuqpgMdNQBO0Mr660Z5qOJ0ukx'
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        # Invalid payload
        print('INVALID PAYLOAD')
        return {}, 400
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        print('INVALID SIGNATURE')
        return {}, 400

    # Handle the checkout.session.completed event
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        print(session)
        line_items = stripe.checkout.Session.list_line_items(session['id'], limit=1)
        print(line_items['data'][0]['description'])

    return {}
