var bleno = require('bleno');

var BlenoPrimaryService = bleno.PrimaryService;

var wi_serial = require('./serial-chara');

var SerialChara = new wi_serial();

console.log('bleno - WiSerial');

bleno.on('stateChange', function(state) {
  console.log('on -> stateChange: ' + state);

  if (state === 'poweredOn') {
    console.log(SerialChara.uuid);
    bleno.startAdvertising('WiSerial', [SerialChara.uuid]);
  } else {
    bleno.stopAdvertising();
  }
});

bleno.on('advertisingStart', function(error) {
  console.log('on -> advertisingStart: ' + (error ? 'error ' + error : 
'success'));

  if (!error) {
    bleno.setServices([
      new BlenoPrimaryService({
        uuid: SerialChara.uuid,
        characteristics: [
          SerialChara
        ]
      })
    ]);
  }
});
