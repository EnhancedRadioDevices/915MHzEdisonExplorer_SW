var util = require('util');

var bleno = require('../..');
var BlenoPrimaryService = bleno.PrimaryService;

var SerialNumberCharacteristic = require('./serial-number-characteristic');
var HardwareRevisionCharacteristic = require('./hardware-revision-characteristic');

function DeviceInformationService(ws) {
  DeviceInformationService.super_.call(this, {
    uuid: '180a',
    characteristics: [
      new SerialNumberCharacteristic(ws),
      new HardwareRevisionCharacteristic(ws)
    ]
  });
}

util.inherits(DeviceInformationService, BlenoPrimaryService);

module.exports = DeviceInformationService;