=========
Changelog
=========

2.0.1 (2021-01-21)
------------------

* Add serial+I2C operating modes to read_iss_mode()

2.0.0 (2019-11-04)
------------------

* BREAKING CHANGE: Use 7-bit I2C device addresses

1.0.0 (2019-10-16)
------------------

* BREAKING CHANGE: Remember the previous IO state in the setup_* methods (thanks SamP20)
* BREAKING CHANGE: Improve the serial mode API
* Add verbose logging option

0.3.1 (2018-07-02)
------------------

* Fix Python2 serial interface

0.3.0 (2018-05-28)
------------------

* Add SPI support
* Add Serial UART support
* Improve test coverage

0.2.4 (2018-05-23)
------------------

* Add SPI, Serial and IO setup methods

0.2.3 (2018-05-22)
------------------

* Fix and test Travis PyPI auto-deploy


0.2.0 (2018-05-21)
------------------

* Generate documentation
* Add dummy driver option for test purposes
* Configure I/O as input by default
* Add i2c.read/write aliases for read_ad1/write_ad1
* Update setup_i2c to split out clk_khz and use_i2c_hardware parameters


0.1.0 (2018-04-19)
------------------

* Initial release
