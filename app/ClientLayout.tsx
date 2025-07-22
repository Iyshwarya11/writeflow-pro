'use client';
import { SessionProvider, useSession } from "next-auth/react";
import { useEffect } from "react";

function UpsertUserOnLogin() {
  const { data: session } = useSession();
  useEffect(() => {
    if (session?.user?.email) {
      // Send all available user fields
      const userPayload = {
        email: session.user.email,
        ...(session.user.name ? { full_name: session.user.name } : {}),
        ...(session.user.image ? { avatar: session.user.image } : {}),
      };
      fetch('/api/users/upsert', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(userPayload),
      });
    }
  }, [session?.user?.email, session?.user?.name, session?.user?.image]);
  return null;
}

export default function ClientLayout({ children }: { children: React.ReactNode }) {
  return (
    <SessionProvider>
      <UpsertUserOnLogin />
      {children}
    </SessionProvider>
  );
} 