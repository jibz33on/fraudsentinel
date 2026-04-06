-- FraudSentinel Seed Data
-- Golden dataset: 6 users, 8 transactions across 6 fraud scenarios
-- All transactions start PENDING — agents will update to APPROVED/REVIEW/REJECTED

DO $$
DECLARE
  jimmy_id    UUID;
  mark_id     UUID;
  sarah_id    UUID;
  priya_id    UUID;
  alex_id     UUID;
  techcorp_id UUID;
BEGIN

  -- ── Users ──────────────────────────────────────────────────────────────────

  INSERT INTO users (name, email, avg_spend, usual_location, usual_hours, transaction_count, account_age_days, risk_profile)
  VALUES ('Jimmy K', 'jimmy@test.com', 85.00, 'Kochi, India', '9am-10pm', 284, 547, 'low')
  RETURNING id INTO jimmy_id;

  INSERT INTO users (name, email, avg_spend, usual_location, usual_hours, transaction_count, account_age_days, risk_profile)
  VALUES ('Mark T', 'mark@test.com', 45.00, 'Kochi, India', '8am-9pm', 156, 820, 'low')
  RETURNING id INTO mark_id;

  INSERT INTO users (name, email, avg_spend, usual_location, usual_hours, transaction_count, account_age_days, risk_profile)
  VALUES ('Sarah M', 'sarah@test.com', 200.00, 'London, UK', '10am-11pm', 423, 1200, 'low')
  RETURNING id INTO sarah_id;

  INSERT INTO users (name, email, avg_spend, usual_location, usual_hours, transaction_count, account_age_days, risk_profile)
  VALUES ('Priya S', 'priya@test.com', 200.00, 'Singapore', '9am-10pm', 98, 320, 'medium')
  RETURNING id INTO priya_id;

  INSERT INTO users (name, email, avg_spend, usual_location, usual_hours, transaction_count, account_age_days, risk_profile)
  VALUES ('Alex R', 'alex@test.com', 0.00, 'Mumbai, India', 'unknown', 0, 1, 'medium')
  RETURNING id INTO alex_id;

  INSERT INTO users (name, email, avg_spend, usual_location, usual_hours, transaction_count, account_age_days, risk_profile)
  VALUES ('TechCorp Ltd', 'techcorp@test.com', 9500.00, 'Dubai, UAE', '8am-6pm', 1240, 1825, 'low')
  RETURNING id INTO techcorp_id;

  -- ── Transactions ───────────────────────────────────────────────────────────

  -- Scenario 1: OBVIOUS FRAUD — unknown location, high amount, crypto exchange
  INSERT INTO transactions (id, user_id, amount, currency, merchant, location, ip_address, device, status)
  VALUES ('txn-4821', jimmy_id, 4500.00, 'USD', 'Crypto Exchange XY', 'Lagos, Nigeria', '197.210.1.1', 'iPhone 14', 'PENDING');

  -- Scenario 2: NORMAL — matches user profile exactly
  INSERT INTO transactions (id, user_id, amount, currency, merchant, location, ip_address, device, status)
  VALUES ('txn-4822', mark_id, 45.00, 'INR', 'Swiggy', 'Kochi, India', '103.21.1.1', 'Samsung S21', 'PENDING');

  -- Scenario 3: AMBIGUOUS — amount higher than avg but merchant/location match
  INSERT INTO transactions (id, user_id, amount, currency, merchant, location, ip_address, device, status)
  VALUES ('txn-4823', sarah_id, 890.00, 'GBP', 'Amazon UK', 'London, UK', '82.45.1.1', 'MacBook Pro', 'PENDING');

  -- Scenario 4a: VELOCITY FRAUD — 5 rapid transactions (1 of 5)
  INSERT INTO transactions (id, user_id, amount, currency, merchant, location, ip_address, device, status, created_at)
  VALUES ('txn-4824', priya_id, 200.00, 'SGD', 'Lazada', 'Singapore', '175.41.1.1', 'iPad Pro', 'PENDING', NOW());

  -- Scenario 4b: VELOCITY FRAUD (2 of 5, ~2 mins later)
  INSERT INTO transactions (id, user_id, amount, currency, merchant, location, ip_address, device, status, created_at)
  VALUES ('txn-4825', priya_id, 200.00, 'SGD', 'Lazada', 'Singapore', '175.41.1.1', 'iPad Pro', 'PENDING', NOW() + INTERVAL '2 minutes');

  -- Scenario 4c: VELOCITY FRAUD (3 of 5, ~4 mins later)
  INSERT INTO transactions (id, user_id, amount, currency, merchant, location, ip_address, device, status, created_at)
  VALUES ('txn-4826', priya_id, 200.00, 'SGD', 'Lazada', 'Singapore', '175.41.1.1', 'iPad Pro', 'PENDING', NOW() + INTERVAL '4 minutes');

  -- Scenario 5: NEW USER — large first transaction is suspicious
  INSERT INTO transactions (id, user_id, amount, currency, merchant, location, ip_address, device, status)
  VALUES ('txn-4827', alex_id, 2000.00, 'INR', 'Flipkart', 'Mumbai, India', '49.36.1.1', 'OnePlus 11', 'PENDING');

  -- Scenario 6: HIGH BUT NORMAL — large amount matches business profile
  INSERT INTO transactions (id, user_id, amount, currency, merchant, location, ip_address, device, status)
  VALUES ('txn-4828', techcorp_id, 10000.00, 'USD', 'AWS', 'Dubai, UAE', '185.220.1.1', 'Windows PC', 'PENDING');

  RAISE NOTICE 'Seed data inserted successfully';
  RAISE NOTICE '6 users created';
  RAISE NOTICE '8 transactions created (6 scenarios)';

END $$;
