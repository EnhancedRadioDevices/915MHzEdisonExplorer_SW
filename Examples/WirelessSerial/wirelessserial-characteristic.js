var util = require('util');

var bleno = require('bleno');

var BlenoCharacteristic = bleno.Characteristic;
var BlenoDescriptor = bleno.Descriptor;

function WsCharacteristic() {
  WsCharacteristic.super_.call(this, {
    uuid: '2a25',
    properties: ['read', 'write'],
    value: '0002',
    descriptors: [
      new BlenoDescriptor({
        uuid: '2901',
        value: 'serial number'
      })
    ]
  });
}

util.inherits(WsCharacteristic, BlenoCharacteristic);

module.exports = WsCharacteristic;
