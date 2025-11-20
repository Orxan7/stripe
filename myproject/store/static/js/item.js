async function redirectToCheckout(url, itemId, stripeKey) {
    const response = await fetch(url);
    const data = await response.json();

    const stripe = Stripe(stripeKey);

    stripe.redirectToCheckout({
        sessionId: data.session_id
    });
}