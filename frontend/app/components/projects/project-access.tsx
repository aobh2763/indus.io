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
interface GrantFormState {
  userId: string;
  accessLevel: AccessLevel;
  canClone: boolean;
}

function GrantAccessForm({ projectId }: { projectId: string }) {
  const grantAccess = useGrantProjectAccess(projectId);
  const [form, setForm] = useState<GrantFormState>({
    userId: '',
    accessLevel: 'VIEWER',
    canClone: false,
  });
  const [expanded, setExpanded] = useState(false);

  const isSubmitting = grantAccess.isPending;

  const handleGrant = () => {
    if (!form.userId.trim()) return;
    const dto: CreateProjectAccessRequest = {
      user_id: form.userId.trim(),
      access_level: form.accessLevel,
      can_clone: form.canClone,
    };
    grantAccess.mutate(dto, {
      onSuccess: () => {
        setForm({ userId: '', accessLevel: 'VIEWER', canClone: false });
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
        Grant Access to a User
      </Button>
    );
  }

  return (
    <div className="rounded-lg border bg-muted/30 p-4 space-y-4">
      <p className="text-sm font-medium flex items-center gap-2">
        <Plus className="h-4 w-4" /> Grant New Access
      </p>

      {/* User ID input */}
      <div className="grid gap-1.5">
        <Label htmlFor="access-uid" className="text-xs text-muted-foreground">
          User ID (UUID)
        </Label>
        <Input
          id="access-uid"
          value={form.userId}
          onChange={(e) => setForm((f) => ({ ...f, userId: e.target.value }))}
          placeholder="550e8400-e29b-41d4-a716-446655440000"
          className="font-mono text-xs"
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
            <SelectTrigger>
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="VIEWER">Viewer – read-only</SelectItem>
              <SelectItem value="COLLABORATOR">Collaborator – can modify</SelectItem>
              <SelectItem value="SUPERVISOR">Supervisor – supervise</SelectItem>
              <SelectItem value="OWNER">Owner – full control</SelectItem>
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
          disabled={isSubmitting || !form.userId.trim()}
        >
          {isSubmitting && <Loader2 className="mr-2 h-3 w-3 animate-spin" />}
          Grant Access
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
      <DialogContent className="sm:max-w-[580px] max-h-[80vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <ShieldAlert className="h-5 w-5 text-muted-foreground" />
            Manage Access
          </DialogTitle>
          <DialogDescription>
            Control who can view, edit, or administer this project.
          </DialogDescription>
        </DialogHeader>

        <Separator />

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
                <TableHead className="text-center">Clone</TableHead>
                <TableHead className="text-right">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {accessList.map((entry) => (
                <TableRow key={entry.id}>
                  {/* Avatar + truncated UUID */}
                  <TableCell>
                    <div className="flex items-center gap-2">
                      <Avatar className="h-7 w-7">
                        <AvatarFallback className="text-xs">
                          {entry.user_id.slice(0, 2).toUpperCase()}
                        </AvatarFallback>
                      </Avatar>
                      <span className="font-mono text-xs text-muted-foreground truncate max-w-[120px]">
                        {entry.user_id}
                      </span>
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
                      disabled={isMutating}
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
                            <code className="font-mono text-xs">
                              {entry.user_id}
                            </code>
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