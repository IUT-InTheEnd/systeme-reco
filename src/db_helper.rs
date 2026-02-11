use postgres::{Client, NoTls, Error};

pub fn connection_db() -> Result<Client, Error> {
    Client::connect("host=localhost user=InTheEnd_User password=InTheEnd_Password dbname=InTheEnd_DB port=25000", NoTls)
}