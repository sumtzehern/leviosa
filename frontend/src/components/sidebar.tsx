
import { useEffect, useState } from "react";
import { NavLink } from "react-router-dom";
import { FileText, Database, Menu, X } from "lucide-react";
import { Button } from "./ui/button";
import { cn } from "@/lib/utils";
import { ThemeToggle } from "./theme-toggle";

const navLinks = [
  {
    title: "Parse Document",
    href: "/",
    icon: FileText,
  },
  {
    title: "Extract Data",
    href: "/extract",
    icon: Database,
  },
];

export function Sidebar() {
  const [isMobileOpen, setIsMobileOpen] = useState(false);
  const [isMobile, setIsMobile] = useState(false);

  useEffect(() => {
    const checkScreenSize = () => {
      setIsMobile(window.innerWidth < 768);
    };

    // Initial check
    checkScreenSize();

    // Add event listener
    window.addEventListener('resize', checkScreenSize);

    // Cleanup
    return () => {
      window.removeEventListener('resize', checkScreenSize);
    };
  }, []);

  const toggleSidebar = () => {
    setIsMobileOpen(!isMobileOpen);
  };

  const closeMobileSidebar = () => {
    if (isMobile) {
      setIsMobileOpen(false);
    }
  };

  return (
    <>
      {/* Mobile menu toggle */}
      {isMobile && (
        <Button 
          variant="ghost" 
          size="icon" 
          className="fixed top-4 left-4 z-50 md:hidden"
          onClick={toggleSidebar}
        >
          {isMobileOpen ? <X /> : <Menu />}
        </Button>
      )}
      
      {/* Sidebar */}
      <aside 
        className={cn(
          "bg-sidebar border-r border-sidebar-border h-screen flex flex-col w-60 fixed left-0 top-0 z-40 transition-transform duration-300 md:translate-x-0",
          isMobile && !isMobileOpen && "-translate-x-full"
        )}
      >
        {/* Logo & App Title */}
        <div className="flex items-center gap-2 px-4 h-16 border-b border-sidebar-border">
          <div className="bg-marine p-1 rounded">
            <svg 
              width="24" 
              height="24" 
              viewBox="0 0 24 24" 
              fill="none" 
              xmlns="http://www.w3.org/2000/svg"
              className="text-white"
            >
              <path 
                d="M7 21H3C2.44772 21 2 20.5523 2 20V4C2 3.44772 2.44772 3 3 3H7M14 3V21M14 3H7M14 3H21C21.5523 3 22 3.44772 22 4V20C22 20.5523 21.5523 21 21 21H14M14 21H7M7 3V21" 
                stroke="currentColor" 
                strokeWidth="2" 
                strokeLinecap="round" 
              />
            </svg>
          </div>
          <h1 className="font-semibold text-lg text-sidebar-foreground">Leviosa</h1>
        </div>

        {/* Navigation */}
        <nav className="flex-1 py-4 overflow-y-auto">
          <ul className="space-y-1 px-2">
            {navLinks.map((link) => (
              <li key={link.href}>
                <NavLink
                  to={link.href}
                  className={({ isActive }) => cn(
                    "flex items-center gap-3 px-3 py-2 rounded-md transition-colors",
                    isActive 
                      ? "bg-sidebar-accent text-sidebar-accent-foreground font-medium" 
                      : "text-sidebar-foreground/80 hover:bg-sidebar-accent/50"
                  )}
                  onClick={closeMobileSidebar}
                >
                  <link.icon size={18} />
                  <span>{link.title}</span>
                </NavLink>
              </li>
            ))}
          </ul>
        </nav>

        {/* Bottom section */}
        <div className="p-4 border-t border-sidebar-border flex justify-between items-center">
          <span className="text-xs text-sidebar-foreground/60">v1.0.0</span>
          <ThemeToggle />
        </div>
      </aside>
      
      {/* Backdrop for mobile */}
      {isMobile && isMobileOpen && (
        <div 
          className="fixed inset-0 bg-background/80 backdrop-blur-sm z-30 md:hidden"
          onClick={closeMobileSidebar}
        />
      )}
    </>
  );
}
