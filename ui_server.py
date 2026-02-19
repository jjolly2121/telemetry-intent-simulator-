@app.route("/intent", methods=["POST"])
def submit_intent():

    data = request.json

    # 1. Structural validation
    validate_schema(data)

    # 2. Domain validation
    validate_domain(data, system_state)

    # 3. Inject as PENDING
    intent_manager.submit_intent(...)