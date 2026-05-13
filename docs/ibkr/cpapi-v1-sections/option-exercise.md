### Exercise Options Copy Location

The operation to exercise via Client Portal is quite involved, and requires that users confirm details across multiple websocket requests.

To initiate the process, developers must make a handshake request passing the “exercise” argument. Then, users will pass in their Option’s ConID to the “CEX” field.

Developers should also maintain [Live Order Updates](/campus/ibkr-api-page/cpapi-v1/#ws-order-updates-sub) while exercising options to confirm final results.

```
shs+exercise+{"CEX":"Your_Option_Conid"}
```

This will initially respond with the acknowledgement of the topic.

You will then receive additional messages about the available options to proceed with, including “Cancel” or “Submit”. This will also offer contract information, position information, and an ID to track the request with.

We may also receive a warning notification about this Option exercise, such as in-the-money warnings. This do not need to be suppressed or replied to; however, they should be noted by the trader as they come through.

```
{"topic":"shs+exercise"}

{"data":{"user_action":[{"id":"submit","text":"Submit"},{"id":"cancel","text":"Cancel"}],"underlying_price":"$211.35","contract":"**AAPL** JUN 28 '24 192.5 Call","underlying_symbol":"AAPL","exercise":{"confirm":false,"confirm_final":false,"enabled":true},"revocable":false,"loading":true,"hold":{"confirm":false,"enabled":true},"qty_lapse":0,"submitted":0,"qty_hold":0,"sec_type":"OPT","qty_exercise":0,"underlying_conid":"265598","morning_expiration":false,"id":5,"position":50,"deadline":"16:25"},"action":"content","MID":"14","topic":"shs+exercise"}

{"data":{"submitted":0,"qty_hold":0,"qty_exercise":0,"warning":"Currently the option is in-the-money by the amount of 18.85 (more than 5 ticks)","exercise":{"confirm":false,"enabled":true},"revocable":false,"loading":false,"qty_lapse":0},"action":"content","MID":"17","topic":"shs+exercise"}
```

After receiving our second listed message above, we can construct our exercise request. This will use the “inp” topic, along with the exercise argument once again.

Within the brackets, we will pass the “user\_input” as our action, and then the data field will contian the order parameters. This will include our ID, which we retrieved from our prior shs+exercise response. We’ll then pass “submit” as our user\_action, and then pass our exercise options.

The critical values to observe here are whether you would like your exercise to be final, with “make\_final”:true. We also submit our quantity of options to exercise with the “value” parameter. In this case, we are exercising 5 shares.

```
inp+exercise+{"action":"user_input","data":{"id":"5","user_action":"submit","exercise":{"allowed":"not_shown","make_final":true,"value":5}}}
```

If there are any additional confirmation/warnings then they will be provided on a new message, including a new “id” value.

```
{"data":{"user_actions":[{"id":"continue","text":"Continue"},{"id":"cancel","text":"Cancel"}],"id":7,"text":"This exercise request will be final and irreversible. Once submitted, the option position and the stock position will update immediately.","title":"Warning"},"MID":"19","action":"prompt","topic":"inp+exercise"}
```

As we noticed above, we now would need to request that our exercise continue for id 7 again using the inp+exercise topic.

```
inp+exercise+{"action":"user_input","data":{"id":"7","user_action":"continue"}
```

Once the developer submits the new ID with “continue” as their user\_action, they will see the order submitted in the SOR websocket.

```
{"topic":"sor","args":[{"acct":"DU1234567","conidex":"708764406","conid":708764406,"account":"DU1234567","orderId":827785484,"cashCcy":"USD","sizeAndFills":"0/5","orderDesc":"EXERCISE 5, Day","description1":"AAPL","description2":"JUN 28 '24 192.5 Call","ticker":"AAPL","secType":"OPT","remainingQuantity":5.0,"filledQuantity":0.0,"totalSize":5.0,"companyName":"APPLE INC","status":"Inactive","order_ccp_status":"Pending Submit","supportsTaxOpt":"1","lastExecutionTime":"240624150344","bgColor":"#000000","fgColor":"#AFAFAF","isEventTrading":"0","lastExecutionTime_r":1719241424000,"side":"EXER"}]}
```
