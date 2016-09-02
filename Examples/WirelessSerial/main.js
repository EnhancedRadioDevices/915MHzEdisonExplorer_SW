var WS = require('node-wirelessserial');

var bleno = require('../..');

var DeviceInformationService = require('./device-information-service');
var WSService = require('./wirelessserial-service');

var ws = new WS();

var deviceInformationService = new DeviceInformationService(ws);
var wsService = new WSService(ws);

bleno.on('stateChange', function(state) {
  console.log('on -> stateChange: ' + state);

  if (state === 'poweredOn') {
    bleno.startAdvertising('ws', [wsService.uuid]);
  } else {
    bleno.stopAdvertising();
  }
});

bleno.on('advertisingStart', function(error) {
  console.log('on -> advertisingStart: ' + (error ? 'error ' + error : 'success'));
  
  if (!error) {
    bleno.setServices([
      deviceInformationService,
      wsService
    ]);
  }
});