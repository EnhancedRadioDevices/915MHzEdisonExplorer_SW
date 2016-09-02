var util = require('util');

var bleno = require('../..');
var BlenoCharacteristic = bleno.Characteristic;
var BlenoDescriptor = bleno.Descriptor;

function HardwareRevisionCharacteristic(ws) {
  HardwareRevisionCharacteristic.super_.call(this, {
    uuid: '2a27',
    properties: ['read'],
    descriptors: [
      new BlenoDescriptor({
        uuid: '2901',
        value: 'ws(1) version'
      })
    ]
  });

  this.ws = ws;
}

util.inherits(HardwareRevisionCharacteristic, BlenoCharacteristic);

HardwareRevisionCharacteristic.prototype.onReadRequest = function(offset, callback) {
  if (offset) {
    callback(this.RESULT_ATTR_NOT_LONG, null);
  } else {
    this.ws.version(function(version) {
      callback(this.RESULT_SUCCESS, new Buffer(version));
    }.bind(this));
  }
};

module.exports = HardwareRevisionCharacteristic;