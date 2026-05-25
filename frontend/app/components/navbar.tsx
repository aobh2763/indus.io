"use client";

import { Menu } from "lucide-react";
import { useAuthStore } from "~/features/auth/auth.store"; // adjust path as needed

import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "~/components/ui/accordion";
import { Button } from "~/components/ui/button";
import {
  NavigationMenu,
  NavigationMenuContent,
  NavigationMenuItem,
  NavigationMenuLink,
  NavigationMenuList,
  NavigationMenuTrigger,
} from "~/components/ui/navigation-menu";
import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
  SheetTrigger,
} from "~/components/ui/sheet";

interface MenuItem {
  title: string;
  url: string;
  description?: string;
  icon?: React.ReactNode;
  items?: MenuItem[];
}

interface Navbar1Props {
  className?: string;
  logo?: {
    url: string;
    title: string;
    className?: string;
  };
  menu?: MenuItem[];
  auth?: {
    login: {
      title: string;
      url: string;
    };
    signup: {
      title: string;
      url: string;
    };
  };
}

const Navbar1 = ({
  logo = {
    url: "/",
    title: "Indus.io",
  },
  menu = [
    { title: "Dashboard", url: "/" },
    { title: "Projects", url: "/projects-management" },
    { title: "Pipeline", url: "/pipeline-builder" },
  ],
  auth = {
    login: { title: "Login", url: "/login" },
    signup: { title: "Sign up", url: "/signup" },
  },
}: Navbar1Props) => {
  const { isAuthenticated, isHydrated, user, logout } = useAuthStore();

  const renderAuthButtons = () => {
    // Avoid hydration mismatch — render nothing until store is ready
    if (!isHydrated) return null;

    if (isAuthenticated && user) {
      return (
        <div className="flex items-center gap-2">
          <span className="text-sm text-muted-foreground truncate max-w-[100px]">
            {user.email ?? user.name}
          </span>
          <Button variant="outline" onClick={logout}>
            Logout
          </Button>
        </div>
      );
    }

    return (
      <>
        <Button asChild variant="outline">
          <a href={auth.login.url}>{auth.login.title}</a>
        </Button>
        <Button asChild>
          <a href={auth.signup.url}>{auth.signup.title}</a>
        </Button>
      </>
    );
  };

  const renderMobileAuthButtons = () => {
    if (!isHydrated) return null;

    if (isAuthenticated && user) {
      return (
        <div className="flex flex-col gap-3">
          <span className="text-sm text-muted-foreground">
            {user.email ?? user.name}
          </span>
          <Button variant="outline" onClick={logout}>
            Logout
          </Button>
        </div>
      );
    }

    return (
      <div className="flex flex-col gap-3">
        <Button asChild variant="outline">
          <a href={auth.login.url}>{auth.login.title}</a>
        </Button>
        <Button asChild>
          <a href={auth.signup.url}>{auth.signup.title}</a>
        </Button>
      </div>
    );
  };

  return (
    <div className="fixed left-0 right-0 top-4 z-50 mx-auto w-full max-w-3xl rounded-full px-8 py-3 bg-card">
      {/* Desktop Menu */}
      <nav className="hidden items-center justify-between lg:flex lg:gap-10">
        <div className="flex items-center justify-between flex-5">
          {/* Logo */}
          <a href={logo.url} className="flex items-center gap-2">
            <span className="text-lg font-semibold tracking-tighter">
              {logo.title}
            </span>
          </a>
          <div className="flex items-center">
            <NavigationMenu>
              <NavigationMenuList className="gap-2">
                {menu.map((item) => renderMenuItem(item))}
              </NavigationMenuList>
            </NavigationMenu>
          </div>
        </div>
        <div className="flex flex-1 gap-2">
          {renderAuthButtons()}
        </div>
      </nav>

      {/* Mobile Menu */}
      <div className="block lg:hidden">
        <div className="flex items-center justify-between">
          <Sheet>
            <SheetTrigger asChild>
              <Button variant="outline" size="icon">
                <Menu className="size-4" />
              </Button>
            </SheetTrigger>
            <SheetContent className="overflow-y-auto">
              <SheetHeader>
                <SheetTitle>
                  <a href={logo.url} className="flex items-center gap-2">
                    <span className="text-lg font-semibold tracking-tighter">
                      {logo.title}
                    </span>
                  </a>
                </SheetTitle>
              </SheetHeader>
              <div className="flex flex-col gap-6 p-4">
                <Accordion
                  type="single"
                  collapsible
                  className="flex w-full flex-col gap-4"
                >
                  {menu.map((item) => renderMobileMenuItem(item))}
                </Accordion>
                {renderMobileAuthButtons()}
              </div>
            </SheetContent>
          </Sheet>
        </div>
      </div>
    </div>
  );
};

const renderMenuItem = (item: MenuItem) => {
  if (item.items) {
    return (
      <NavigationMenuItem key={item.title}>
        <NavigationMenuTrigger>{item.title}</NavigationMenuTrigger>
        <NavigationMenuContent className="bg-popover text-popover-foreground">
          {item.items.map((subItem) => (
            <NavigationMenuLink asChild key={subItem.title} className="w-80">
              <SubMenuLink item={subItem} />
            </NavigationMenuLink>
          ))}
        </NavigationMenuContent>
      </NavigationMenuItem>
    );
  }

  return (
    <NavigationMenuItem key={item.title}>
      <NavigationMenuLink
        href={item.url}
        className="px-4 py-2 text-sm font-medium transition-colors hover:bg-muted hover:text-accent-foreground"
      >
        {item.title}
      </NavigationMenuLink>
    </NavigationMenuItem>
  );
};

const renderMobileMenuItem = (item: MenuItem) => {
  if (item.items) {
    return (
      <AccordionItem key={item.title} value={item.title} className="border-b-0">
        <AccordionTrigger className="text-md py-0 font-semibold hover:no-underline">
          {item.title}
        </AccordionTrigger>
        <AccordionContent className="mt-2">
          {item.items.map((subItem) => (
            <SubMenuLink key={subItem.title} item={subItem} />
          ))}
        </AccordionContent>
      </AccordionItem>
    );
  }

  return (
    <a key={item.title} href={item.url} className="text-md font-semibold">
      {item.title}
    </a>
  );
};

const SubMenuLink = ({ item }: { item: MenuItem }) => {
  return (
    <a
      className="flex min-w-80 flex-row gap-4 rounded-md p-3 leading-none no-underline transition-colors outline-none select-none hover:bg-muted hover:text-accent-foreground"
      href={item.url}
    >
      <div className="text-foreground">{item.icon}</div>
      <div>
        <div className="text-sm font-semibold">{item.title}</div>
        {item.description && (
          <p className="text-sm leading-snug text-muted-foreground">
            {item.description}
          </p>
        )}
      </div>
    </a>
  );
};

export { Navbar1 };
