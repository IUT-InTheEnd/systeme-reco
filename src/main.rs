mod db_helper;
mod basics_function;
mod reco_user_based_p1;

use postgres::{Client, NoTls, Error};


fn main() -> Result<(), Error> {
    let mut client = Client::connect("host=localhost user=InTheEnd_User password=InTheEnd_Password dbname=InTheEnd_DB port=25000", NoTls)?;

    for row in client.query("SELECT user_id, user_pseudo, user_job FROM sae5_6.user", &[])? {
        let id: i32 = row.get(0);
        let pseudo: &str = row.get(1);
        let job: &str = row.get(2);

        println!("{} {} {}", id, pseudo, job);
    }
    Ok(())
}
