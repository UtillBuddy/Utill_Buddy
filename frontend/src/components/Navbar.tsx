import Link from "next/link";

export default function Navbar() {
  return (
    <nav className="bg-surface shadow-md">
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between py-4">
          <Link href="/dashboard">
            <a className="text-2xl font-bold text-primary">Email Sender</a>
          </Link>
          <div className="flex items-center space-x-4">
            <Link href="/dashboard">
              <a className="text-secondary hover:text-primary">Dashboard</a>
            </Link>
            <Link href="/template">
              <a className="text-secondary hover:text-primary">Template</a>
            </Link>
            <Link href="/select-region">
              <a className="text-secondary hover:text-primary">Send Emails</a>
            </Link>
            <Link href="/email-config">
              <a className="text-secondary hover:text-primary">Settings</a>
            </Link>
            <Link href="/login">
              <a className="px-4 py-2 font-bold text-white bg-primary rounded-md hover:bg-opacity-80">
                Logout
              </a>
            </Link>
          </div>
        </div>
      </div>
    </nav>
  );
}
