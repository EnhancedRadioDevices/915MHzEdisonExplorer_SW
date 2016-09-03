var util = require('util');

var bleno = require('bleno');

var BlenoCharacteristic = bleno.Characteristic;

function SerialChara() {
  SerialChara.super_.call(this, {
    uuid: '8a53fa01d9d242afb942ce50a39bc7e6',
    properties: ['read', 'write', 'notify'],
    value: null
  });

  this._value = new Buffer(0);
  this._updateValueCallback = null;
};

util.inherits(SerialChara, BlenoCharacteristic);

SerialChara.prototype.onReadRequest = function(offset, callback) 
{
  console.log('SerialChara - onReadRequest: value = ' + 
this._value.toString('hex'));

  callback(this.RESULT_SUCCESS, this._value);
};

SerialChara.prototype.onWriteRequest = function(data, offset, 
withoutResponse, callback) {
  this._value = data;

  console.log('SerialChara - onWriteRequest: value = ' + 
this._value.toString('hex'));

  // TODO: write to pyserial script
  callback(this.RESULT_SUCCESS);
};

SerialChara.prototype.onSubscribe = function(maxValueSize, 
updateValueCallback) {
  console.log('SerialChara - onSubscribe');

  this._updateValueCallback = updateValueCallback;

  // TODO: start pyserial listener
};

SerialChara.prototype.onUnsubscribe = function() {
  console.log('SerialChara - onUnsubscribe');

  this._updateValueCallback = null;

  // TODO: stop pyserial listener
};

module.exports = SerialChara;
