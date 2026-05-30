import { useState } from 'react';
import { Loader2, Plus, ShieldAlert, Trash2, UserPlus } from 'lucide-react';

import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from '~/components/ui/alert-dialog';
import { Avatar, AvatarFallback } from '~/components/ui/avatar';
import { Badge } from '~/components/ui/badge';
import { Button } from '~/components/ui/button';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '~/components/ui/dialog';
import { Input } from '~/components/ui/input';
import { Label } from '~/components/ui/label';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '~/components/ui/select';
import { Separator } from '~/components/ui/separator';
import { Skeleton } from '~/components/ui/skeleton';
import { Switch } from '~/components/ui/switch';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '~/components/ui/table';

import { useProjectUIStore } from '../../features/projects/project.store';
import {
  useGetProjectAccess,
  useGrantProjectAccess,
  useUpdateProjectAccess,
  useRevokeProjectAccess,
} from '../../features/projects/project.hooks';
import type { AccessLevel, CreateProjectAccessRequest } from '../../features/projects/project.schema';

const ACCESS_LEVEL_LABEL: Record<AccessLevel, string> = {
  OWNER: 'Owner',
  SUPERVISOR: 'Supervisor',
  COLLABORATOR: 'Collaborator',
  VIEWER: 'Viewer',
};

const ACCESS_LEVEL_DESCRIPTION: Record<AccessLevel, string> = {
  OWNER: 'Full control: project settings, access management, and cloning.',
  COLLABORATOR: 'Can work on the project and production setup.',
  SUPERVISOR: 'Operational oversight role for monitoring and review.',
  VIEWER: 'Read-only access to project information.',
};
interface GrantFormState {
  recipient: string;
  accessLevel: AccessLevel;
  canClone: boolean;
}

function GrantAccessForm({ projectId }: { projectId: string }) {
  const grantAccess = useGrantProjectAccess(projectId);
  const [form, setForm] = useState<GrantFormState>({
    recipient: '',
    accessLevel: 'VIEWER',
    canClone: false,
  });
  const [expanded, setExpanded] = useState(false);

  const isSubmitting = grantAccess.isPending;

  const handleGrant = () => {
    const recipient = form.recipient.trim();
    if (!recipient) return;

    const dto: CreateProjectAccessRequest = {
      ...(recipient.includes('@') ? { email: recipient } : { user_id: recipient }),
      access_level: form.accessLevel,
      can_clone: form.canClone,
    };

    grantAccess.mutate(dto, {
      onSuccess: () => {
        setForm({ recipient: '', accessLevel: 'VIEWER', canClone: false });
        setExpanded(false);
      },
    });
  };

  if (!expanded) {
    return (
      <Button
        variant="outline"
        size="sm"
        className="w-full border-dashed"
        onClick={() => setExpanded(true)}
      >
        <UserPlus className="mr-2 h-4 w-4" />
        Invite Contributor
      </Button>
    );
  }

  return (
    <div className="rounded-lg border border-neutral-800 bg-black/30 p-4 space-y-4">
      <p className="text-sm font-medium flex items-center gap-2">
        <Plus className="h-4 w-4" /> Invite Contributor
      </p>

      <div className="grid gap-1.5">
        <Label htmlFor="access-uid" className="text-xs text-muted-foreground">
          Contributor email or user ID
        </Label>
        <Input
          id="access-uid"
          value={form.recipient}
          onChange={(e) => setForm((f) => ({ ...f, recipient: e.target.value }))}
          placeholder="amina.haddad@indus.example"
          className="text-xs"
        />
      </div>
      <div className="flex gap-3">
        <div className="grid gap-1.5 flex-1">
          <Label className="text-xs text-muted-foreground">Access Level</Label>
          <Select
            value={form.accessLevel}
            onValueChange={(v) =>
              setForm((f) => ({ ...f, accessLevel: v as AccessLevel }))
            }
          >
          <SelectTrigger className="w-full">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="VIEWER">Viewer - read-only</SelectItem>
              <SelectItem value="COLLABORATOR">Collaborator - can modify</SelectItem>
              <SelectItem value="SUPERVISOR">Supervisor - monitor/review</SelectItem>
              <SelectItem value="OWNER">Owner - full control</SelectItem>
            </SelectContent>
          </Select>
        </div>

        <div className="grid gap-1.5">
          <Label className="text-xs text-muted-foreground">Can Clone</Label>
          <div className="flex h-10 items-center">
            <Switch
              checked={form.canClone}
              onCheckedChange={(v) => setForm((f) => ({ ...f, canClone: v }))}
            />
          </div>
        </div>
      </div>

      <div className="flex gap-2 justify-end">
        <Button
          variant="ghost"
          size="sm"
          onClick={() => setExpanded(false)}
          disabled={isSubmitting}
        >
          Cancel
        </Button>
        <Button
          size="sm"
          onClick={handleGrant}
          disabled={isSubmitting || !form.recipient.trim()}
        >
          {isSubmitting && <Loader2 className="mr-2 h-3 w-3 animate-spin" />}
          Invite Contributor
        </Button>
      </div>
    </div>
  );
}

export function ProjectAccessDialog() {
  const { isAccessDialogOpen, accessProjectId, closeAccessDialog } = useProjectUIStore();

  const pid = accessProjectId ?? '';
  const { data: accessList = [], isLoading } = useGetProjectAccess(pid);
  const updateAccess = useUpdateProjectAccess(pid);
  const revokeAccess = useRevokeProjectAccess(pid);

  const isMutating = updateAccess.isPending || revokeAccess.isPending;

  return (
    <Dialog
      open={isAccessDialogOpen}
      onOpenChange={(o) => !o && closeAccessDialog()}
    >
      <DialogContent className="border-neutral-800 bg-neutral-950 text-neutral-200 sm:max-w-[820px] max-h-[84vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <ShieldAlert className="h-5 w-5 text-muted-foreground" />
            Manage Access
          </DialogTitle>
          <DialogDescription>
            Control who can view, edit, or administer this project.
          </DialogDescription>
        </DialogHeader>

        <div className="grid grid-cols-1 gap-2 rounded-lg border border-neutral-800 bg-black/30 p-3 text-xs text-neutral-500 sm:grid-cols-2">
          {(Object.keys(ACCESS_LEVEL_DESCRIPTION) as AccessLevel[]).map((level) => (
            <div key={level}>
              <span className="font-medium text-neutral-300">{ACCESS_LEVEL_LABEL[level]}</span>
              <span className="ml-1">{ACCESS_LEVEL_DESCRIPTION[level]}</span>
            </div>
          ))}
        </div>

        {/* Member table */}
        {isLoading ? (
          <div className="space-y-2 py-2">
            {[...Array(3)].map((_, i) => (
              <div key={i} className="flex items-center gap-3">
                <Skeleton className="h-8 w-8 rounded-full" />
                <Skeleton className="h-4 w-48" />
                <Skeleton className="ml-auto h-7 w-24" />
              </div>
            ))}
          </div>
        ) : accessList.length === 0 ? (
          <p className="py-6 text-center text-sm text-muted-foreground">
            No access entries yet. Grant access below.
          </p>
        ) : (
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>User</TableHead>
                <TableHead>Level</TableHead>
                <TableHead>Status</TableHead>
                <TableHead className="text-center">Clone</TableHead>
                <TableHead className="text-right">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {accessList.map((entry) => (
                <TableRow key={entry.id}>
                  <TableCell>
                    <div className="flex items-center gap-2">
                      <Avatar className="h-7 w-7">
                        <AvatarFallback className="text-xs">
                          {(entry.user_name || entry.user_email || entry.user_id).slice(0, 2).toUpperCase()}
                        </AvatarFallback>
                      </Avatar>
                      <div className="min-w-0">
                        <p className="truncate text-sm font-medium">
                          {entry.user_name || entry.user_email || 'Unknown user'}
                        </p>
                        <p className="truncate text-xs text-muted-foreground max-w-[170px]">
                          {entry.user_email || entry.user_id}
                        </p>
                      </div>
                    </div>
                  </TableCell>

                  {/* Inline access level select */}
                  <TableCell>
                    <Select
                      value={entry.access_level}
                      onValueChange={(v) =>
                        updateAccess.mutate({
                          accessId: entry.id,
                          data: { access_level: v as AccessLevel },
                        })
                      }
                      disabled={isMutating}
                    >
                      <SelectTrigger className="h-7 w-32 text-xs">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="VIEWER">Viewer</SelectItem>
                        <SelectItem value="COLLABORATOR">Collaborator</SelectItem>
                        <SelectItem value="SUPERVISOR">Supervisor</SelectItem>
                        <SelectItem value="OWNER">Owner</SelectItem>
                      </SelectContent>
                    </Select>
                  </TableCell>

                  <TableCell>
                    <Badge
                      variant="outline"
                      className={
                        entry.status === 'ACCEPTED'
                          ? 'border-emerald-500/20 bg-emerald-500/10 text-emerald-400'
                          : 'border-amber-500/20 bg-amber-500/10 text-amber-400'
                      }
                    >
                      {entry.status}
                    </Badge>
                  </TableCell>

                  {/* Clone toggle */}
                  <TableCell className="text-center">
                    <Switch
                      checked={entry.can_clone}
                      onCheckedChange={(v) =>
                        updateAccess.mutate({
                          accessId: entry.id,
                          data: { can_clone: v },
                        })
                      }
                      disabled={isMutating || entry.status !== 'ACCEPTED'}
                      className="scale-90"
                    />
                  </TableCell>

                  {/* Revoke */}
                  <TableCell className="text-right">
                    <AlertDialog>
                      <AlertDialogTrigger asChild>
                        <Button
                          variant="ghost"
                          size="icon"
                          className="h-7 w-7 text-muted-foreground hover:text-destructive"
                        >
                          <Trash2 className="h-3.5 w-3.5" />
                        </Button>
                      </AlertDialogTrigger>
                      <AlertDialogContent>
                        <AlertDialogHeader>
                          <AlertDialogTitle>Revoke Access</AlertDialogTitle>
                          <AlertDialogDescription>
                            This will remove all permissions for user{' '}
                            <span className="font-medium">
                              {entry.user_email || entry.user_name || entry.user_id}
                            </span>
                            . They will lose access to this project immediately.
                          </AlertDialogDescription>
                        </AlertDialogHeader>
                        <AlertDialogFooter>
                          <AlertDialogCancel>Cancel</AlertDialogCancel>
                          <AlertDialogAction
                            className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
                            onClick={() => revokeAccess.mutate(entry.id)}
                          >
                            Revoke
                          </AlertDialogAction>
                        </AlertDialogFooter>
                      </AlertDialogContent>
                    </AlertDialog>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        )}

        <Separator />
        {accessProjectId && <GrantAccessForm projectId={accessProjectId} />}
      </DialogContent>
    </Dialog>
  );
}
